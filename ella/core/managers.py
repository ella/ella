from datetime import datetime

from django.db import models, transaction
from django.db.models import F
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import smart_str

from ella.core.cache import cache_this
from ella.core.cache.invalidate import CACHE_DELETER


DEFAULT_LISTING_PRIORITY = getattr(settings, 'DEFAULT_LISTING_PRIORITY', 0)


class RelatedManager(models.Manager):
    """
    A shortcut to enable using select_related by default on models.
    """
    def get_query_set(self):
        return super(RelatedManager, self).get_query_set().select_related()

def invalidate_listing(key, self, *args, **kwargs):
    CACHE_DELETER.register_test(self.model, '', key)

def get_listings_key(func, self, category=None, count=10, offset=1, mods=[], content_types=[], **kwargs):
    c = category and  category.id or ''

    return 'ella.core.managers.ListingManager.get_listing:%s:%d:%d:%s:%s:%s' % (
            c, count, offset,
            ','.join('.'.join((model._meta.app_label, model._meta.object_name)) for model in mods),
            ','.join(map(str, content_types)),
            ','.join(':'.join((k, smart_str(v))) for k, v in kwargs.items()),
)

class PlacementManager(models.Manager):
    def get_static_placements(self, category):
        now = datetime.now()
        return self.filter(models.Q(publish_to__gt=now) | models.Q(publish_to__isnull=True),  publish_from__lt=now, category=category, static=True)

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

    def get_queryset(self, category=None, children=NONE, mods=[], content_types=[], **kwargs):
        now = datetime.now()
        qset = self.filter(publish_from__lte=now, **kwargs)

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
            qset = qset.filter(placement__publishable__content_type__in=([ ContentType.objects.get_for_model(m) for m in mods ] + content_types))

        return qset.exclude(publish_to__lt=now)

    @cache_this(get_listings_key, invalidate_listing)
    def get_listing(self, category=None, children=NONE, count=10, offset=1, mods=[], content_types=[], unique=None, **kwargs):
        """
        Get top objects for given category and potentionally also its child categories.

        Params:
            category - Category object to list objects for. None if any category will do
            count - number of objects to output, defaults to 10
            offset - starting with object number... 1-based
            mods - list of Models, if empty, object from all models are included
            **kwargs - rest of the parameter are passed to the queryset unchanged
        """
        # TODO try to write  SQL (.extra())
        assert offset > 0, "Offset must be a positive integer"
        assert count >= 0, "Count must be a positive integer"

        if not count:
            return []

        now = datetime.now()
        qset = self.get_queryset(category, children, mods, content_types, **kwargs)

        # listings with active priority override
        active = models.Q(
                    priority_value__isnull=False,
                    priority_from__isnull=False,
                    priority_from__lte=now,
                    priority_to__gte=now
        )

        qsets = (
            # modded-up objects
            qset.filter(active, priority_value__gt=DEFAULT_LISTING_PRIORITY).order_by('-priority_value', '-publish_from'),
            # default priority
            qset.exclude(active).order_by('-publish_from'),
            # modded-down priority
            qset.filter(active, priority_value__lt=DEFAULT_LISTING_PRIORITY).order_by('-priority_value', '-publish_from'),
        )

        out = []

        # templates are 1-based, compensate
        offset -= 1
        limit = offset + count

        # take out not unwanted objects
        if unique:
            listed_targets = unique.copy()
        else:
            listed_targets = set([])

        # iterate through qsets until we have enough objects
        for q in qsets:
            data = q
            if data:
                for l in data:
                    tgt = l.placement_id
                    if tgt in listed_targets:
                        continue
                    listed_targets.add(tgt)
                    out.append(l)
                    if len(out) == limit:
                        return out[offset:limit]
        return out[offset:offset + count]

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
            self._count = self.manager.get_queryset(**self._kwargs).count()
        return self._count


def get_top_objects_key(func, self, count, mods=[]):
    return 'ella.core.managers.HitCountManager.get_top_objects_key:%d:%d:%s' % (
            settings.SITE_ID, count, ','.join(['.'.join((model._meta.app_label, model._meta.object_name)) for model in mods])
        )

class HitCountManager(models.Manager):

    def hit(self, placement):
        count = self.filter(placement=placement).update(hits=F('hits')+1)

        if count < 1:
            hc = self.create(placement=placement, hits=1)

    @cache_this(get_top_objects_key)
    def get_top_objects(self, count, mods=[]):
        """
        Return count top rated objects. Cache this for 10 minutes without any chance of cache invalidation.
        """
        kwa = {}
        if mods:
            kwa['placement__target_ct__in'] = [ ContentType.objects.get_for_model(m) for m in mods ]
        return list(self.filter(placement__category__site=settings.SITE_ID, **kwa).order_by('-hits')[:count])
