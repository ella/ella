from datetime import datetime, timedelta

from django.db import models
from django.db.models import F, Q
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import smart_str

from ella.core.cache import cache_this
from ella.core.cache.invalidate import CACHE_DELETER
from ella.core.conf import core_settings


class RelatedManager(models.Manager):
    def get_related_for_object(self, obj, count, mods=[], only_from_same_site=True):
        from ella.core.models import Publishable

        # manually entered dependencies

        qset = Publishable.objects.filter(
                related__related_ct=ContentType.objects.get_for_model(obj),
                related__related_id=obj.pk
            )
        if mods:
            ct_ids = [ContentType.objects.get_for_model(m).pk for m in mods]
            qset = qset.filter(content_type__in=ct_ids)
        if only_from_same_site:
            qset = qset.filter(category__site__pk=settings.SITE_ID)
        related = list(qset[:count])

        if len(related) >= count:
            return related

        count -= len(related)

        # related objects via tags
        try:
            from tagging.models import TaggedItem
            if TaggedItem._meta.installed:
                # we are only tagging Publishables, not individual content types
                if isinstance(obj, Publishable):
                    obj = obj.publishable_ptr

                qset = Publishable.objects.filter(
                        placement__publish_from__lte=datetime.now(),
                    ).distinct()
                if mods:
                    qset = qset.filter(content_type__in=ct_ids)
                if only_from_same_site:
                    qset = qset.filter(category__site__pk=settings.SITE_ID)

                #print qset
                #print TaggedItem.objects.all()
                to_add = TaggedItem.objects.get_related(obj, qset, num=count+len(related))
                #print to_add
                for rel in to_add:
                    if rel != obj and rel not in related:
                        count -= 1
                        related.append(rel)
                    if count <= 0:
                        return related
        except ImportError, e:
            pass

        # top objects in given category
        if count > 0:
            from ella.core.models import Listing
            cat = obj.category
            listings = Listing.objects.get_listing(category=cat, count=count+len(related), mods=mods)
            for l in listings:
                t = l.target
                if t != obj and t not in related:
                    related.append(t)
                    count -= 1

                if count <= 0:
                    return related

        return related


def invalidate_listing(key, self, *args, **kwargs):
    CACHE_DELETER.register_test(self.model, '', key)

def get_listings_key(func, self, category=None, count=10, offset=1, mods=[], content_types=[], **kwargs):
    c = category and  category.id or ''

    return 'ella.core.managers.ListingManager.get_listing:%s:%d:%d:%s:%s:%s' % (
            c, count, offset,
            ','.join(str(model._meta) for model in mods),
            ','.join(map(str, content_types)),
            ','.join(':'.join((k, smart_str(v))) for k, v in kwargs.items()),
    )

class PlacementManager(models.Manager):
    def get_query_set(self, *args, **kwargs):
        qset = super(PlacementManager, self).get_query_set(*args, **kwargs).select_related('publishable')
        return qset

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

    def get_query_set(self, *args, **kwargs):
        # get all the fields you typically need to render listing
        qset = super(ListingManager, self).get_query_set(*args, **kwargs).select_related(
                'placement',
                'placement__category',
                'placement__publishable',
                'placement__publishable__category',
                'placement__publishable__content_type'
            )
        return qset

    def get_listing_queryset(self, category=None, children=NONE, mods=[], content_types=[], now=None, **kwargs):
        if not now:
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
            [now] - datetime used instead of default datetime.now() value
            [unique] - set of already listed Placement IDs
            **kwargs - rest of the parameter are passed to the queryset unchanged
        """
        def mark_before_output(output):
            for l in output:
                listed_targets.add(l.placement_id)

        def make_items_unique(qset):

            out = []
            listed_targets_now = set()
            for l in qset:
                tgt = l.placement_id
                if tgt in listed_targets or tgt in listed_targets_now:
                    continue
                listed_targets_now.add(tgt)
                out.append(l)
                if len(out) == limit:
                    result = out[offset:limit]
                    mark_before_output(result)
                    return result
            mark_before_output(out)
            return out

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

        # take out unwanted objects
        if unique is not None:
            listed_targets = unique.copy()
        else:
            listed_targets = set([])

        # only use priorities if somebody wants them
        if not core_settings.USE_PRIORITIES:
            if unique is not None:
                return make_items_unique(qset)
            return qset[offset:limit]

        # listings with active priority override
        active = models.Q(
                    priority_value__isnull=False,
                    priority_from__isnull=False,
                    priority_from__lte=now,
                    priority_to__gte=now
        )

        qsets = (
            # modded-up objects
            qset.filter(active, priority_value__gt=core_settings.DEFAULT_LISTING_PRIORITY).order_by('-priority_value', '-publish_from'),
            # default priority
            qset.exclude(active).order_by('-publish_from'),
            # modded-down priority
            qset.filter(active, priority_value__lt=core_settings.DEFAULT_LISTING_PRIORITY).order_by('-priority_value', '-publish_from'),
        )

        out = []

        # iterate through qsets until we have enough objects
        for q in qsets:
            data = q.iterator()
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
            self._count = self.manager.get_listing_queryset(**self._kwargs).count()
        return self._count


def get_top_objects_key(func, self, count, days=None, mods=[]):
    return 'ella.core.managers.HitCountManager.get_top_objects_key:%d:%d:%s:%s' % (
            settings.SITE_ID, count, str(days), ','.join('.'.join(str(model._meta) for model in mods))
        )

class HitCountManager(models.Manager):

    def hit(self, placement):
        count = self.filter(placement=placement).update(hits=F('hits')+1)

        if count < 1:
            self.create(placement=placement, hits=1)

    @cache_this(get_top_objects_key)
    def get_top_objects(self, count, days=None, mods=[]):
        """
        Return count top rated objects. Cache this for 10 minutes without any chance of cache invalidation.
        """
        qset = self.filter(placement__category__site=settings.SITE_ID).order_by('-hits')

        if mods:
            qset = qset.filter(placement__publishable__content_type__in = [ ContentType.objects.get_for_model(m) for m in mods ])

        now = datetime.now()
        if days is None:
            qset = qset.filter(placement__publish_from__lte=now)
        else:
            start = now - timedelta(days=days)
            qset = qset.filter(placement__publish_from__range=(start, now,))
        qset = qset.filter(Q(placement__publish_to__gt=now) | Q(placement__publish_to__isnull=True))

        return list(qset[:count])
