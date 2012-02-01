from datetime import datetime

from django.db import models
from django.core.exceptions import ImproperlyConfigured
from django.contrib.contenttypes.models import ContentType
from django.utils.importlib import import_module
from django.utils.encoding import smart_str

from ella.core.cache import cache_this
from ella.core.conf import core_settings


class RelatedManager(models.Manager):
    def get_related_for_object(self, obj, count, finder=core_settings.DEFAULT_RELATED_FINDER,
        mods=[], only_from_same_site=True):
        """
        Returns at most ``count`` publishable objects related to ``obj`` using
        named related finder ``finder``.
        
        If only specific type of publishable is prefered, use ``mods`` attribute
        to list required classes.
        
        Finally, use ``only_from_same_site`` if you don't want cross-site
        content.
        
        ``finder`` atribute uses ``RELATED_FINDERS`` settings to find out
        what finder function to use. If none is specified, ``DEFAULT_RELATED_FINDER``
        is used to perform the query.  
        """
        if not core_settings.RELATED_FINDERS.has_key(finder):
            raise ImproperlyConfigured('Named finder %r specified but cannot be '
                'found in RELATED_FINDERS settings.' % finder)

        finder_modstr = core_settings.RELATED_FINDERS[finder]
        module, attr = finder_modstr.rsplit('.', 1)
        try:
            mod = import_module(module)
        except ImportError, e:
            raise ImproperlyConfigured('Error importing related finder %s: "%s"' % (finder_modstr, e))
        try:
            finder_func = getattr(mod, attr)
        except AttributeError, e:
            raise ImproperlyConfigured('Error importing related finder %s: "%s"' % (finder_modstr, e))

        return finder_func(obj, count, mods, only_from_same_site)


def get_listings_key(func, self, category=None, count=10, offset=1, mods=[], content_types=[], **kwargs):
    c = category and  category.id or ''

    return 'ella.core.managers.ListingManager.get_listing:%s:%d:%d:%s:%s:%s' % (
            c, count, offset,
            ','.join(str(model._meta) for model in mods),
            ','.join(map(str, content_types)),
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

    def get_listing_queryset(self, category=None, children=NONE, mods=[], content_types=[], now=None, **kwargs):
        if not now:
            now = datetime.now()
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
        if mods or content_types:
            qset = qset.filter(publishable__content_type__in=([ ContentType.objects.get_for_model(m) for m in mods ] + content_types))

        return qset.exclude(publish_to__lt=now).order_by('-publish_from')

    @cache_this(get_listings_key)
    def get_listing(self, category=None, children=NONE, count=10, offset=1, mods=[], content_types=[], **kwargs):
        """
        Get top objects for given category and potentionally also its child categories.

        Params:
            category - Category object to list objects for. None if any category will do
            count - number of objects to output, defaults to 10
            offset - starting with object number... 1-based
            mods - list of Models, if empty, object from all models are included
            [now] - datetime used instead of default datetime.now() value
            **kwargs - rest of the parameter are passed to the queryset unchanged
        """
        # TODO try to write  SQL (.extra())
        assert offset > 0, "Offset must be a positive integer"
        assert count >= 0, "Count must be a positive integer"

        if not count:
            return []

        now = datetime.now()
        if 'now' in kwargs:
            now = kwargs.pop('now')
        qset = self.get_listing_queryset(category, children, mods, content_types, now, **kwargs)

        # templates are 1-based, compensate
        offset -= 1
        limit = offset + count

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

