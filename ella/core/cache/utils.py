from hashlib import md5
import logging

from django.dispatch import receiver
from django.db.models import ObjectDoesNotExist
from django.db.models.signals import post_save, post_delete
from django.core.cache import cache
from django.http import Http404
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import smart_str
from django.conf import settings


log = logging.getLogger('ella.core.cache.utils')

KEY_PREFIX = 'core.gco'
CACHE_TIMEOUT = getattr(settings, 'CACHE_TIMEOUT', 10*60)

@receiver(post_save)
@receiver(post_delete)
def invalidate_cache(sender, instance, **kwargs):
    key = _get_key(KEY_PREFIX, ContentType.objects.get_for_model(sender), pk=instance.pk)
    cache.delete(key)

def normalize_key(key):
    return md5(key).hexdigest()

def _get_key(start, model, pk=None, **kwargs):
    if pk and not kwargs:
        return ':'.join((
            start, str(model.pk), str(pk)
        ))

    for key, val in kwargs.iteritems():
        if hasattr(val, 'pk'):
            kwargs[key] = val.pk

    return normalize_key(':'.join((
                start,
                str(model.pk),
                ','.join(':'.join((key, smart_str(kwargs[key]))) for key in sorted(kwargs.keys()))
    )))

def get_cached_object(model, timeout=CACHE_TIMEOUT, **kwargs):
    """
    Return a cached object. If the object does not exist in the cache, create it.

    Params:
        model - ContentType instance representing the model's class or the model class itself
        timeout - TTL for the item in cache, defaults to CACHE_TIMEOUT
        **kwargs - lookup parameters for content_type.get_object_for_this_type and for key creation

    Throws:
        model.DoesNotExist is propagated from content_type.get_object_for_this_type
    """
    if not isinstance(model, ContentType):
        model = ContentType.objects.get_for_model(model)

    key = _get_key(KEY_PREFIX, model, **kwargs)

    obj = cache.get(key)
    if obj is None:
        mclass = model.model_class()
        obj = mclass._default_manager.get(**kwargs)
        cache.set(key, obj, timeout)
    return obj

def get_cached_objects(model, pks, timeout=CACHE_TIMEOUT):
    """
    Return a list of objects with given PKs using cache.

    Params:
        model - ContentType instance representing the model's class or the model class itself
        pks - list of Primary Key values to look up
        timeout - TTL for the items in cache, defaults to CACHE_TIMEOUT

    Throws:
        model.DoesNotExist is propagated from content_type.get_object_for_this_type
    """
    if isinstance(model, ContentType):
        model = ContentType.objects.get_for_model(model)

    keys = [_get_key(KEY_PREFIX, model, pk=pk) for pk in pks]

    cached = cache.get_many(keys)

    keys_to_set = set(keys) - set(cached.keys())
    if keys_to_set:
        mclass = model.model_class()
        lookup = dict(zip(keys, pks))
        to_set = {}
        for k in keys_to_set:
            to_set[k] = cached[k] = mclass._default_manager.get(pk=lookup[k])
        cache.set_many(to_set, timeout=timeout)

    return [cached[k] for k in keys]


def get_cached_object_or_404(model, timeout=CACHE_TIMEOUT, **kwargs):
    """
    Shortcut that will raise Http404 if there is no object matching the query

    see get_cached_object for params description
    """
    try:
        return get_cached_object(model, timeout=timeout, **kwargs)
    except ObjectDoesNotExist, e:
        raise Http404('Reason: %s' % str(e))

def cache_this(key_getter, timeout=CACHE_TIMEOUT):
    def wrapped_decorator(func):
        def wrapped_func(*args, **kwargs):
            key = key_getter(*args, **kwargs)
            if key is not None:
                result = cache.get(key)
            else:
                result = None
            if result is None:
                log.debug('cache_this(key=%s), object not cached.', key)
                result = func(*args, **kwargs)
                cache.set(key, result, timeout)
            return result

        wrapped_func.__dict__ = func.__dict__
        wrapped_func.__doc__ = func.__doc__
        wrapped_func.__name__ = func.__name__

        return wrapped_func
    return wrapped_decorator

