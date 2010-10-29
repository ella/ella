from hashlib import md5
import logging

from django.db.models import ObjectDoesNotExist, signals
from django.core.cache import cache
from django.http import Http404
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import smart_str
from django.conf import settings

from ella.core.cache.invalidate import CACHE_DELETER


log = logging.getLogger('ella.core.cache.utils')

KEY_FORMAT_LIST = 'ella.core.cache.utils.get_cached_list'
KEY_FORMAT_OBJECT = 'ella.core.cache.utils.get_cached_object'
CACHE_TIMEOUT = getattr(settings, 'CACHE_TIMEOUT', 10*60)


def delete_cached_object(key, auto_normalize=True):
    """ proxy function for direct object deletion from cache. May be implemented through ActiveMQ in future. """
    if auto_normalize:
        key = normalize_key(key)
    cache.delete(key)

def normalize_key(key):
    return md5(key).hexdigest()

def dump_param(param):
    if hasattr(param, 'pk'):
        return '|'.join((param._meta.app_label, param._meta.object_name, str(param.pk)))
    return smart_str(param)

def _get_key(start, model, kwargs):
    for key, val in kwargs.iteritems():
        if hasattr(val, 'pk'):
            kwargs[key] = val.pk
    return normalize_key(start + ':'.join((
                model._meta.app_label,
                model._meta.object_name,
                ','.join(':'.join((key, dump_param(kwargs[key]))) for key in sorted(kwargs.keys()))
    )))

def get_cached_list(model, *args, **kwargs):
    """
    Return a cached list. If the list does not exist in the cache, create it
    and register it for invalidation if any object from the list is updated (check via _get_pk_val()).

    Params:
        model - Model class ContentType instance representing the model's class
        **kwargs - lookup parameters for content_type.get_object_for_this_type and for key creation

    """
    if isinstance(model, ContentType):
        model = model.model_class()

    key = _get_key(KEY_FORMAT_LIST, model, kwargs)

    l = cache.get(key)
    if l is None:
        log.debug('get_cached_list(model=%s), object not cached.' % str(model))
        l = list(model._default_manager.filter(*args, **kwargs))
        cache.set(key, l, CACHE_TIMEOUT)
        for o in l:
            CACHE_DELETER.register_pk(o, key)
        #CACHE_DELETER.register_test(model, lambda x: model._default_manager.filter(**kwargs).filter(pk=x._get_pk_val()) == 1, key)
    return l

def get_cached_object(model, **kwargs):
    """
    Return a cached object. If the object does not exist in the cache, create it
    and register it for invalidation if the object is updated (check via _get_pk_val().

    Params:
        model - Model class ContentType instance representing the model's class
        **kwargs - lookup parameters for content_type.get_object_for_this_type and for key creation

    Throws:
        model.DoesNotExist is propagated from content_type.get_object_for_this_type
    """
    if isinstance(model, ContentType):
        model = model.model_class()

    key = _get_key(KEY_FORMAT_OBJECT, model, kwargs)

    obj = cache.get(key)
    if obj is None:
        obj = model._default_manager.get(**kwargs)
        cache.set(key, obj, CACHE_TIMEOUT)
        CACHE_DELETER.register_pk(obj, key)
    return obj

def get_cached_object_or_404(model, **kwargs):
    """
    Shortcut that will raise Http404 if there is no object matching the query

    see get_cached_object for params description
    """
    try:
        return get_cached_object(model, **kwargs)
    except ObjectDoesNotExist, e:
        raise Http404('Reason: %s' % str(e))

def cache_this(key_getter, invalidator=None, timeout=CACHE_TIMEOUT):
    def wrapped_decorator(func):
        def wrapped_func(*args, **kwargs):
            key = key_getter(func, *args, **kwargs)
            if key is not None:
                key = normalize_key(key)
                result = cache.get(key)
            else:
                result = None
            if result is None:
                log.debug('cache_this(key=%s), object not cached.' % key)
                result = func(*args, **kwargs)
                cache.set(key, result, timeout)
                if invalidator:
                    invalidator(key, *args, **kwargs)
            return result

        wrapped_func.__dict__ = func.__dict__
        wrapped_func.__doc__ = func.__doc__
        wrapped_func.__name__ = func.__name__

        return wrapped_func
    return wrapped_decorator

class CacheInvalidator(object):
    def __init__(self, *filter_fields):
        self.filter_fields = filter_fields or ('pk',)

    def __call__(self, sender, instance, **kwargs):
        if not kwargs.get('created', False):
            filter_kwargs = dict((k, getattr(instance, k))
                for k in self.filter_fields)
            key = _get_key(KEY_FORMAT_OBJECT, sender, filter_kwargs)
            delete_cached_object(key, auto_normalize=False)

def register_cache_invalidator(model, *filter_fields):
    cache_invalidator = CacheInvalidator(*filter_fields)
    signals.post_delete.connect(cache_invalidator, sender=model, weak=False)
    signals.post_save.connect(cache_invalidator, sender=model, weak=False)

from django.db.models.fields.related import ForeignKey, ReverseSingleRelatedObjectDescriptor

class CachedForeignKey(ForeignKey):
    def contribute_to_class(self, cls, name):
        super(CachedForeignKey, self).contribute_to_class(cls, name)
        setattr(cls, self.name, CachedReverseSingleRelatedObjectDescriptor(self))
        #register_cache_invalidator(self.rel.to)

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

from django.contrib.contenttypes.generic import GenericForeignKey

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
