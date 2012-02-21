from datetime import datetime

from django.db import models
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module
from django.utils.encoding import smart_str

from ella.core.cache import cache_this, redis
from ella.core.conf import core_settings

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
            if gathered: collected += gathered
            if len(collected) >= count:
                return collected[:count]

        return collected

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
        if finder is None:
            finder = 'default'

        if not core_settings.RELATED_FINDERS.has_key(finder):
            raise ImproperlyConfigured('Named finder %r specified but cannot be '
                'found in RELATED_FINDERS settings.' % finder)

        # accept non-iterables too (single member named finders) 
        finders_modstr = core_settings.RELATED_FINDERS[finder]
        if not hasattr(finders_modstr, '__iter__'):
            finders_modstr = (finders_modstr,)

        # gather all functions before actual use to prevent import errors
        # during the real process
        finder_funcs = []
        for finder_modstr in finders_modstr:
            module, attr = finder_modstr.rsplit('.', 1)
            try:
                mod = import_module(module)
            except ImportError, e:
                raise ImproperlyConfigured('Error importing related finder %s: "%s"' % (finder_modstr, e))
            try:
                finder_func = getattr(mod, attr)
            except AttributeError, e:
                raise ImproperlyConfigured('Error importing related finder %s: "%s"' % (finder_modstr, e))
            finder_funcs.append(finder_func)

        return self.collect_related(finder_funcs, obj, count, mods, only_from_same_site)


def get_listings_key(self, category=None, count=10, offset=1, content_types=[], date_range=(), **kwargs):
    c = category and  category.id or ''

    return 'core.get_listing:%s:%d:%d:%s:%s:%s' % (
            c, count, offset,
            ','.join(map(lambda ct: str(ct.pk), content_types)),
            ','.join(map(lambda d: d.strftime('%Y%m%d'), date_range)),
            ','.join(':'.join((k, smart_str(v))) for k, v in kwargs.items()),
    )

class ListingManager(models.Manager):
    NONE = 0
    IMMEDIATE = 1
    ALL = 2

    def clean_listings(self):
        """
        Method that cleans the Listing model by deleting all listings that are no longer valid.
        Should be run periodicaly to purge the DB from unneeded data.
        """
        self.filter(publish_to__lt=datetime.now()).delete()

    def get_query_set(self, *args, **kwargs):
        # get all the fields you typically need to render listing
        qset = super(ListingManager, self).get_query_set(*args, **kwargs).select_related(
                'publishable',
                'publishable__category',
                'publishable__content_type'
            )
        return qset

    def get_listing_queryset(self, category=None, children=NONE, content_types=[], date_range=(), **kwargs):
        # give the database some chance to cache this query
        now = datetime.now().replace(second=0, microsecond=0)

        if date_range:
            qset = self.filter(publish_from__range=date_range, publishable__published=True, **kwargs)
        else:
            qset = self.filter(publish_from__lte=now, publishable__published=True, **kwargs)

        if category:
            if children == self.NONE:
                # only this one category
                qset = qset.filter(category=category)
            elif children == self.IMMEDIATE:
                # this category and its children
                qset = qset.filter(models.Q(category__tree_parent=category) | models.Q(category=category))
            elif children == self.ALL:
                # this category and all its descendants
                qset = qset.filter(category__tree_path__startswith=category.tree_path, category__site=category.site_id)

            else:
                raise AttributeError('Invalid children value (%s) - should be one of (%s, %s, %s)' % (children, self.NONE, self.IMMEDIATE, self.ALL))

        # filtering based on Model classes
        if content_types:
            qset = qset.filter(publishable__content_type__in=content_types)

        return qset.exclude(publish_to__lt=now).order_by('-publish_from')

    @cache_this(get_listings_key)
    def get_listing(self, category=None, children=NONE, count=10, offset=1, content_types=[], date_range=(), **kwargs):
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
        assert offset > 0, "Offset must be a positive integer"
        assert count >= 0, "Count must be a positive integer"

        if not count:
            return []

        # templates are 1-based, compensate
        offset -= 1
        limit = offset + count

        if redis.client and not kwargs and len(content_types) <= 1:
            return redis.get_listing(category, children, count, offset, content_types, date_range)

        qset = self.get_listing_queryset(category, children, content_types, date_range, **kwargs)

        # direct listings, we don't need to check for duplicates
        if children == self.NONE:
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
            if skip <= 2:
                break

        return out

    def get_queryset_wrapper(self, kwargs):
        return ListingQuerySetWrapper(self, kwargs)

class ListingQuerySetWrapper(object):
    def __init__(self, manager, kwargs):
        self.manager = manager
        self._kwargs = kwargs

    def __getitem__(self, k):
        if not isinstance(k, slice) or (k.start is None or k.start < 0) or (k.stop is None  or k.stop < k.start):
            raise TypeError, '%s, %s' % (k.start, k.stop)

        offset = k.start + 1
        count = k.stop - k.start

        return self.manager.get_listing(offset=offset, count=count, **self._kwargs)

    def count(self):
        if not hasattr(self, '_count'):
            self._count = self.manager.get_listing_queryset(**self._kwargs).count()
        return self._count

