from django.db.models import ObjectDoesNotExist
from django.db.models.fields.related import ForeignKey, ReverseSingleRelatedObjectDescriptor
from django.contrib.contenttypes.generic import GenericForeignKey

from ella.core.cache.utils import get_cached_object

class CachedForeignKey(ForeignKey):
    def contribute_to_class(self, cls, name):
        super(CachedForeignKey, self).contribute_to_class(cls, name)
        setattr(cls, self.name, CachedReverseSingleRelatedObjectDescriptor(self))

class CachedReverseSingleRelatedObjectDescriptor(ReverseSingleRelatedObjectDescriptor):
    def __get__(self, instance, instance_type=None):
        if instance is None:
            raise AttributeError, "%s must be accessed via instance" % self.field.name
        cache_name = self.field.get_cache_name()
        try:
            return getattr(instance, cache_name)
        except AttributeError:
            val = getattr(instance, self.field.attname)
            if val is None:
                # If NULL is an allowed value, return it.
                if self.field.null:
                    return None
                raise self.field.rel.to.DoesNotExist
            rel_obj = get_cached_object(self.field.rel.to, pk=val)
            setattr(instance, cache_name, rel_obj)
            return rel_obj

try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^ella\.core\.cache\.fields\.CachedForeignKey"])
except ImportError:
    pass


class CachedGenericForeignKey(GenericForeignKey):
    def __get__(self, instance, instance_type=None):
        # Fix for django 1.0 Admin Validation
        if instance is None:
            # TODO: hotfixed
            #raise AttributeError, u"%s must be accessed via instance" % self.name
            return

        try:
            return getattr(instance, self.cache_attr)
        except AttributeError:
            rel_obj = None

            # Make sure to use ContentType.objects.get_for_id() to ensure that
            # lookups are cached (see ticket #5570). This takes more code than
            # the naive ``getattr(instance, self.ct_field)``, but has better
            # performance when dealing with GFKs in loops and such.
            f = self.model._meta.get_field(self.ct_field)
            ct_id = getattr(instance, f.get_attname(), None)
            if ct_id:
                ct = self.get_content_type(id=ct_id)
                try:
                    rel_obj = get_cached_object(ct, pk = getattr(instance, self.fk_field))
                except ObjectDoesNotExist:
                    pass
            setattr(instance, self.cache_attr, rel_obj)
            return rel_obj

