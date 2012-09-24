from operator import attrgetter

from django.db import models
from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import smart_str
from django.db.models.loading import get_model
from django.conf import settings

from ella.core.cache import cache_this
from ella.core.conf import core_settings
from ella.utils import timezone, import_module_member


class PublishableManager(models.Manager):
    def current(self, now=None):
        now = timezone.now().replace(second=0, microsecond=0)

        return self.filter(
            models.Q(publish_to__isnull=True) | models.Q(publish_to__gt=now),
            published=True, publish_from__lte=now
        )


class CategoryManager(models.Manager):
    _cache = {}
    _hierarchy = {}

    def get_for_id(self, pk):
        try:
            return self.__class__._cache[settings.SITE_ID][pk]
        except KeyError:
            cat = self.get(pk=pk)
            self._add_to_cache(cat)
            return cat

    def get_by_tree_path(self, tree_path):
        try:
            return self.__class__._cache[settings.SITE_ID][tree_path]
        except KeyError:
            cat = self.get(site=settings.SITE_ID, tree_path=tree_path)
            self._add_to_cache(cat)
            return cat

    def _add_to_cache(self, category):
        cache = self.__class__._cache.setdefault(category.site_id, {})
        # pk and tree_path can never clash, safe to store in one dict
        cache[category.pk] = category
        cache[category.tree_path] = category

    def clear_cache(self):
        self.__class__._cache.clear()
        self.__class__._hierarchy.clear()

    def _load_hierarchy(self, site_id):
        cache = self.__class__._cache.setdefault(site_id, {})
        hierarchy = self.__class__._hierarchy.setdefault(site_id, {})
        for c in self.filter(site=site_id).order_by('title'):
            # make sure we are working with the instance already in cache
            c = cache.setdefault(c.id, c)
            hierarchy.setdefault(c.tree_parent_id, []).append(c)

    def _retrieve_children(self, category):
        if not self.__class__._hierarchy:
            self._load_hierarchy(category.site_id)
        return self.__class__._hierarchy[category.site_id].get(category.pk, [])

    def get_children(self, category, recursive=False):
        #make sure this is the instance stored in our cache
        self._add_to_cache(category)
        # copy the returned list. if recursive, we extend it below
        children = self._retrieve_children(category)[:]
        if recursive:
            to_process = children[:]
            while to_process:
                grand_children = self._retrieve_children(to_process.pop())
                children.extend(grand_children)
                to_process.extend(grand_children)
            children = sorted(children, key=attrgetter('tree_path'))
        return children


class RelatedManager(models.Manager):
    def collect_related(self, finder_funcs, obj, count, *args, **kwargs):
        """
        Collects objects related to ``obj`` using a list of ``finder_funcs``.
        Stops when required count is collected or the function list is
        exhausted.
        """
        collected = []
        for func in finder_funcs:
            gathered = func(obj, count, collected, *args, **kwargs)
            if gathered:
                collected += gathered
            if len(collected) >= count:
                return collected[:count]

        return collected

    def _get_finders(self, finder):
        if not hasattr(self, '_finders'):
            self._finders = {}
            for key, finders_modstr in core_settings.RELATED_FINDERS.items():
                # accept non-iterables too (single member named finders)
                if not hasattr(finders_modstr, '__iter__'):
                    finders_modstr = (finders_modstr,)

                # gather all functions before actual use to prevent import errors
                # during the real process
                finder_funcs = []
                for finder_modstr in finders_modstr:
                    finder_funcs.append(import_module_member(finder_modstr, 'related finder'))

                self._finders[key] = finder_funcs

        if finder is None:
            finder = 'default'

        if not finder in self._finders:
            raise ImproperlyConfigured('Named finder %r specified but cannot be '
                'found in RELATED_FINDERS settings.' % finder)
        return self._finders[finder]

    def get_related_for_object(self, obj, count, finder=None, mods=[], only_from_same_site=True):
        """
        Returns at most ``count`` publishable objects related to ``obj`` using
        named related finder ``finder``.

        If only specific type of publishable is prefered, use ``mods`` attribute
        to list required classes.

        Finally, use ``only_from_same_site`` if you don't want cross-site
        content.

        ``finder`` atribute uses ``RELATED_FINDERS`` settings to find out
        what finder function to use. If none is specified, ``default``
        is used to perform the query.
        """
        return self.collect_related(self._get_finders(finder), obj, count, mods, only_from_same_site)


class ListingHandler(object):
    NONE = 0
    IMMEDIATE = 1
    ALL = 2

    @classmethod
    def regenerate(cls, today=None):
        pass

    def __init__(self, category, children=NONE, content_types=[],
                 date_range=(), exclude=None, **kwargs):
        self.category = category
        self.children = children
        self.content_types = content_types
        self.date_range = date_range
        self.exclude = exclude
        self.kwargs = kwargs

    def __getitem__(self, k):
        if isinstance(k, int):
            return self.get_listing(k)

        if not isinstance(k, slice) or k.step:
            raise TypeError, '%s, %s' % (k.start, k.stop)

        offset = k.start or 0

        if offset < 0 or k.stop is None  or k.stop < offset:
            raise TypeError, '%s, %s' % (k.start, k.stop)

        count = k.stop - offset

        return self.get_listings(offset, count)

    def get_listings(self, offset=0, count=10):
        raise NotImplementedError

    def get_listing(self, i):
        return self.get_listings(i, i + 1)[0]

    def count(self):
        raise NotImplementedError

    def __len__(self):
        return self.count()


def get_listings_key(self, category=None, children=ListingHandler.NONE, count=10, offset=0, content_types=[], date_range=(), exclude=None, **kwargs):
    c = category and  category.id or ''

    return 'core.get_listing:%s:%d:%d:%d:%d:%s:%s:%s' % (
            c, count, offset, children, exclude.id if exclude else 0,
            ','.join(map(lambda ct: str(ct.pk), content_types)),
            ','.join(map(lambda d: d.strftime('%Y%m%d'), date_range)),
            ','.join(':'.join((k, smart_str(v))) for k, v in kwargs.items()),
    )


class ListingManager(models.Manager):
    def clean_listings(self):
        """
        Method that cleans the Listing model by deleting all listings that are no longer valid.
        Should be run periodicaly to purge the DB from unneeded data.
        """
        self.filter(publish_to__lt=timezone.now()).delete()

    def get_query_set(self, *args, **kwargs):
        # get all the fields you typically need to render listing
        qset = super(ListingManager, self).get_query_set(*args, **kwargs).select_related(
                'publishable',
                'publishable__category',
            )
        return qset

    def get_listing_queryset(self, category=None, children=ListingHandler.NONE, content_types=[], date_range=(), exclude=None, **kwargs):
        # give the database some chance to cache this query
        now = timezone.now().replace(second=0, microsecond=0)

        if date_range:
            qset = self.filter(publish_from__range=date_range, publishable__published=True, **kwargs)
        else:
            qset = self.filter(publish_from__lte=now, publishable__published=True, **kwargs)

        if category:
            if children == ListingHandler.NONE:
                # only this one category
                qset = qset.filter(category=category)
            elif children == ListingHandler.IMMEDIATE:
                # this category and its children
                qset = qset.filter(models.Q(category__tree_parent=category) | models.Q(category=category))

                for c in category.get_children():
                    if not c.app_data.ella.propagate_listings:
                        qset = qset.exclude(category=c)

            elif children == ListingHandler.ALL:
                # this category and all its descendants
                qset = qset.filter(category__tree_path__startswith=category.tree_path, category__site=category.site_id)

                for c in category.get_children(True):
                    if not c.app_data.ella.propagate_listings:
                        qset = qset.exclude(category__tree_path__startswith=c.tree_path)

            else:
                raise AttributeError('Invalid children value (%s) - should be one of (%s, %s, %s)' % (children, self.NONE, self.IMMEDIATE, self.ALL))

        # filtering based on Model classes
        if content_types:
            qset = qset.filter(publishable__content_type__in=content_types)

        # we were asked to omit certain Publishable
        if exclude:
            qset = qset.exclude(publishable=exclude)

        return qset.exclude(publish_to__lt=now).order_by('-publish_from')

    @cache_this(get_listings_key)
    def get_listing(self, category=None, children=ListingHandler.NONE, count=10, offset=0, content_types=[], date_range=(), exclude=None, **kwargs):
        """
        Get top objects for given category and potentionally also its child categories.

        Params:
            category - Category object to list objects for. None if any category will do
            count - number of objects to output, defaults to 10
            offset - starting with object number... 1-based
            content_types - list of ContentTypes to list, if empty, object from all models are included
            date_range - range for listing's publish_from field
            **kwargs - rest of the parameter are passed to the queryset unchanged
        """
        assert offset >= 0, "Offset must be a positive integer"
        assert count >= 0, "Count must be a positive integer"

        if not count:
            return []

        limit = offset + count

        qset = self.get_listing_queryset(category, children, content_types, date_range, exclude, **kwargs)

        # direct listings, we don't need to check for duplicates
        if children == ListingHandler.NONE:
            return qset[offset:limit]

        seen = set()
        out = []
        while len(out) < count:
            skip = 0
            # 2 i a reasonable value for padding, wouldn't you say dear Watson?
            for l in qset[offset:limit + 2]:
                if l.publishable_id not in seen:
                    seen.add(l.publishable_id)
                    out.append(l)
                    if len(out) == count:
                        break
                else:
                    skip += 1

            # no enough skipped, or not enough listings to work with, no need for another try
            if skip <= 2 or (len(out) + skip) < (count + 2):
                break

            # get another page to fill in the gaps
            offset += count
            limit += count

        return out

    def get_listing_handler(self, source, fallback=True):
        if not hasattr(self, '_listing_handlers'):
            self._listing_handlers = {}
            for k, v in core_settings.LISTING_HANDLERS.items():
                self._listing_handlers[k] = import_module_member(v, 'Listing Handler')

            if 'default' not in self._listing_handlers:
                raise ImproperlyConfigured('You didn\'t specify any default Listing Handler.')

        if source in self._listing_handlers:
            return self._listing_handlers[source]
        elif not fallback:
            return None

        if settings.DEBUG:
            raise ImproperlyConfigured('ListingHandler %s is not defined in settings.' % source)

        return self._listing_handlers['default']

    def get_queryset_wrapper(self, category, children=ListingHandler.NONE,
                             content_types=[], date_range=(), exclude=None,
                             source='default', **kwargs):
        ListingHandler = self.get_listing_handler(source)
        return ListingHandler(
            category, children, content_types, date_range, exclude, **kwargs
        )


class ModelListingHandler(ListingHandler):
    def get_listing(self, i):
        Listing = get_model('core', 'listing')
        return Listing.objects.get_listing_queryset(
                self.category,
                children=self.children,
                content_types=self.content_types,
                date_range=self.date_range,
                exclude=self.exclude
            )[i]

    def get_listings(self, offset=0, count=10):
        Listing = get_model('core', 'listing')
        return Listing.objects.get_listing(
                self.category,
                children=self.children,
                content_types=self.content_types,
                date_range=self.date_range,
                offset=offset,
                count=count,
                exclude=self.exclude
            )

    def count(self):
        if not hasattr(self, '_count'):
            Listing = get_model('core', 'listing')
            self._count = Listing.objects.get_listing_queryset(
                self.category,
                children=self.children,
                content_types=self.content_types,
                date_range=self.date_range,
                exclude=self.exclude
            ).count()
        return self._count

