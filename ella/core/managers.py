from datetime import datetime

from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from ella.core.cache import get_cached_object, cache_this, method_key_getter

DEFAULT_LISTING_PRIORITY = getattr(settings, 'DEFAULT_LISTING_PRIORITY', 0)

class RelatedManager(models.Manager):
    """
    A shortcut to enable using select_related by default on models.
    """
    def get_query_set(self):
        return super(RelatedManager, self).get_query_set().select_related()

def test_listing(*args, **kwargs):
    from ella.core.models import Listing
    return [ (Listing, lambda x: True) ]

class ListingManager(RelatedManager):
    def clean_listings(self):
        """
        Method that cleans the Listing model by deleting all listings that are no longer valid.
        Should be run periodicaly to purge the DB from unneeded data.
        """
        self.filter(remove=True, priority_to__lte=datetime.now()).delete()

    def get_queryset(self, category=None, mods=[], content_types=[], **kwargs):
        now = datetime.now()
        qset = self.exclude(remove=True, priority_to__lte=datetime.now()).filter(publish_from__lte=now, **kwargs)

        if category:
            # only this one category
            qset = qset.filter(category=category)

        # filtering based on Model classes
        if mods or content_types:
            qset = qset.filter(target_ct__in=([ ContentType.objects.get_for_model(m) for m in mods ] + content_types))

        return qset

    def get_count(self, category=None, mods=[], **kwargs):
        return self.get_queryset(category, mods, **kwargs).count()

    @cache_this(method_key_getter, test_listing)
    def get_listing(self, category=None, count=10, offset=1, mods=[], content_types=[], **kwargs):
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
        qset = self.get_queryset(category, mods, content_types, **kwargs).select_related()

        # listings with active priority override
        active = models.Q(priority_from__isnull=False, priority_from__lte=now, priority_to__gte=now)

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

        # iterate through qsets until we have enough objects
        for q in qsets:
            data = q[offset:offset+count]
            if data:
                offset = 0
                out.extend(data)
                count -= len(data)
                if count <= 0:
                    break
            elif offset != 0:
                offset -= q.count()
        return out

def test_hitcount(*args, **kwargs):
    return []

class HitCountManager(models.Manager):
    def hit(self, obj):
        # TODO FIXME: optimizations and thread safety
        target_ct = ContentType.objects.get_for_model(obj)
        hc, created = self.get_or_create(target_ct=target_ct, target_id=obj._get_pk_val())
        if not created:
            hc.hits += 1
        hc.save()

    @cache_this(method_key_getter, test_hitcount)
    def get_top_objects(self, count, mods=[]):
        """
        Return count top rated objects. Cache this for 10 minutes without any chance of cache invalidation.
        """
        kwa = {}
        if mods:
            kwa['target_ct__in'] = [ ContentType.objects.get_for_model(m) for m in mods ]
        return self.filter(site__id=settings.SITE_ID, **kwa)[:count]

class DependencyManager(RelatedManager):
    def report_dependency(self, source, source_key, target, target_key):
        from ella.core.models import Dependency
        source_ct = ContentType.objects.get_for_model(source)
        target_ct = ContentType.objects.get_for_model(target)
        try:
            get_cached_object(
                        Dependency,
                        source_ct=source_ct,
                        source_id=source._get_pk_val(),
                        source_key=source_key,

                        target_ct=target_ct,
                        target_id=target._get_pk_val(),
                        target_key=target_key
)
        except Dependency.DoesNotExist:
            dep = self.create(
                        source_ct=source_ct,
                        source_id=source._get_pk_val(),
                        source_key=source_key,

                        target_ct=target_ct,
                        target_id=target._get_pk_val(),
                        target_key=target_key
)

    def cascade(self, target, key):
        """
        When an object is deleted from cache, this method will invalidate all objects
        dependent on the one being deleted.
        """
        target_ct = ContentType.objects.get_for_model(target)
        qset =  self.filter(
                    target_ct=target_ct,
                    target_key=key
)
        for dep in qset:
            CACHE_DELETER.invalidate(dep.source_ct.model_class(), key)
        qset.delete()

