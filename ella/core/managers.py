from datetime import datetime

from django.db import connection, models, transaction
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

class PlacementManager(RelatedManager):
    def get_static_placements(self, category):
        now = datetime.now()
        return self.filter(models.Q(publish_to__gt=now) | models.Q(publish_to__isnull=True),  publish_from__lt=now, category=category, static=True)

class ListingManager(RelatedManager):
    NONE = 0
    IMMEDIATE = 1
    ALL = 2

    def clean_listings(self):
        """
        Method that cleans the Listing model by deleting all listings that are no longer valid.
        Should be run periodicaly to purge the DB from unneeded data.
        """
        self.filter(remove=True, priority_to__lte=datetime.now()).delete()

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
                qset = qset.filter(category__tree_path__startswith=category.tree_path)
            else:
                raise AttributeError('Invalid children value (%s) - should be one of (%s, %s, %s)' % (children, self.NONE, self.IMMEDIATE, self.ALL))

        # filtering based on Model classes
        if mods or content_types:
            qset = qset.filter(placement__target_ct__in=([ ContentType.objects.get_for_model(m) for m in mods ] + content_types))

        return qset

    def get_count(self, category=None, children=NONE, mods=[], **kwargs):
        now = datetime.now()
        # no longer active listings
        deleted = models.Q(remove=True, priority_to__isnull=False, priority_to__lte=now)
        return self.get_queryset(category, children, mods, **kwargs).exclude(deleted).count()

    @cache_this(get_listings_key, invalidate_listing)
    def get_listing(self, category=None, children=NONE, count=10, offset=1, mods=[], content_types=[], **kwargs):
        """
        Get top objects for given category and potentionally also its child categories.

        Params:
            category - Category object to list objects for. None if any category will do
            count - number of objects to output, defaults to 10
            offset - starting with object number... 1-based
            mods - list of Models, if empty, object from all models are included
            **kwargs - rest of the parameter are passed to the queryset unchanged
        """
        assert offset > 0, "Offset must be a positive integer"
        assert count > 0, "Count must be a positive integer"

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

        # no longer active listings UGLY TERRIBLE HACK DUE TO queryset-refactor not handling .exclude properly
        # FIXME TODO
        deleted = models.Q(remove=True, priority_to__isnull=False, priority_to__lte=now)

        # iterate through qsets until we have enough objects
        for q in qsets:
            data = q.exclude(deleted)[offset:offset+count]
            if data:
                offset = 0
                out.extend(data)
                count -= len(data)
                if count <= 0:
                    break
            elif offset != 0:
                offset -= q.count()
        # HOTFIX only
        if not out:
            return out
        res = []
        listed_targets = []
        for item in out:
            tgt = item.placement.target
            if tgt in listed_targets:
                continue
            listed_targets.append(tgt)
            res.append(item)
        return res

def get_top_objects_key(func, self, count, mods=[]):
    return 'ella.core.managers.HitCountManager.get_top_objects_key:%d:%d:%s' % (
            settings.SITE_ID, count, ''.join(mods)
)

class HitCountManager(models.Manager):

    @transaction.commit_on_success
    def hit(self, placement):
        cursor = connection.cursor()
        res = cursor.execute('UPDATE core_hitcount SET hits=hits+1 WHERE placement_id=%s', (placement.pk,))
        transaction.set_dirty()

        if res < 1:
            hc = self.create(placement=placement)

    @cache_this(get_top_objects_key, timeout=10*60)
    def get_top_objects(self, count, mods=[]):
        """
        Return count top rated objects. Cache this for 10 minutes without any chance of cache invalidation.
        """
        kwa = {}
        if mods:
            kwa['placement__target_ct__in'] = [ ContentType.objects.get_for_model(m) for m in mods ]
        return list(self.filter(placement__category__site=settings.SITE_ID, **kwa)[:count])
