from django.db.models import ObjectDoesNotExist
from django.db.models.fields.related import ForeignKey, ReverseSingleRelatedObjectDescriptor
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.sites.models import SITE_CACHE, Site

from ella.core.cache.utils import get_cached_object

def generate_fk_class(name, retrieve_func, limit_to_model=None):
    class CustomForeignKey(ForeignKey):
        def __init__(self, *args, **kwargs):
            if limit_to_model:
                args = (limit_to_model,) + args
            super(CustomForeignKey, self).__init__(*args, **kwargs)

        def contribute_to_class(self, cls, name):
            super(CustomForeignKey, self).contribute_to_class(cls, name)
            setattr(cls, self.name, CachedReverseSingleRelatedObjectDescriptor(self))

        def south_field_triple(self):
            from south.modelsinspector import introspector
            args, kwargs = introspector(self)
            return ('django.db.models.fields.related.ForeignKey', args, kwargs)

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
                rel_obj = retrieve_func(self.field.rel.to, val)
                setattr(instance, cache_name, rel_obj)
                return rel_obj

    CustomForeignKey.__name__ = name
    return CustomForeignKey

CachedForeignKey = generate_fk_class('CachedForeignKey', lambda m, pk: get_cached_object(m, pk=pk))

def get_site(model, pk):
    try:
        return SITE_CACHE[pk]
    except KeyError:
        SITE_CACHE[pk] = get_cached_object(model, pk=pk)
        return SITE_CACHE[pk]

SiteForeignKey = generate_fk_class('SiteForeignKey', get_site, Site)
ContentTypeForeignKey = generate_fk_class('ContentTypeForeignKey', lambda m, pk: m._default_manager.get_for_id(pk), ContentType)
CategoryForeignKey = generate_fk_class('CategoryForeignKey', lambda m, pk: m._default_manager.get_for_id(pk), 'core.Category')

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
                    rel_obj = get_cached_object(ct, pk=getattr(instance, self.fk_field))
                except ObjectDoesNotExist:
                    pass
            setattr(instance, self.cache_attr, rel_obj)
            return rel_obj

