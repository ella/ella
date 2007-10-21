import md5

try:
    import cPickle as pickle
except ImportError:
    import pickle

from django.db.models import ObjectDoesNotExist
from django.core.cache import cache
from django.http import Http404
from django.contrib.contenttypes.models import ContentType

from ella.core.cache.invalidate import CACHE_DELETER


KEY_FORMAT_LIST = 'ella.core.cache.utils.get_cached_list'
def get_cached_list(model, **kwargs):
    """
    Return a cached list. If the list does not exist in the cache, create it
    and register it for invalidation if any object from the list is updated (check via _get_pk_val()).

    Params:
        model - Model class ContentType instance representing the model's class
        **kwargs - lookup parameters for content_type.get_object_for_this_type and for key creation

    """
    if isinstance(model, ContentType):
        model = model.model_class()

    key = md5.md5(
                pickle.dumps((
                    KEY_FORMAT_LIST,
                    model._meta.app_label,
                    model._meta.object_name.lower(),
                    [ (key, kwargs[key]) for key in sorted(kwargs.keys()) ]
)
)
).hexdigest()

    l = cache.get(key)
    if l is None:
        l = list(model._default_manager.filter(**kwargs))
        cache.set(key, l, 10 * 60)
        CACHE_DELETER.register_test(model, lambda x: model._default_manager.filter(**kwargs).filter(pk=x._get_pk_val()) == 1, key)
    return l

KEY_FORMAT_OBJECT = 'ella.core.cache.utils.get_cached_object'
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

    key = md5.md5(
            pickle.dumps((
                    KEY_FORMAT_OBJECT,
                    model._meta.app_label,
                    model._meta.object_name.lower(),
                    [ (key, kwargs[key]) for key in sorted(kwargs.keys()) ]
)
)
).hexdigest()

    obj = cache.get(key)
    if obj is None:
        obj = model._default_manager.get(**kwargs)
        cache.set(key, obj, 10 * 60)
        CACHE_DELETER.register_pk(obj, key)
    return obj

def get_cached_object_or_404(model, **kwargs):
    """
    Shortcut that will raise Http404 if there is no object matching the query

    see get_cached_object for params description
    """
    try:
        return get_cached_object(model, **kwargs)
    except ObjectDoesNotExist:
        raise Http404

def method_key_getter(func, *args, **kwargs):
    import md5
    return md5.md5(
                pickle.dumps((
                        'ella.core.cache.utils.method_key_getter',
                        func.__module__,
                        func.__name__,
                        args[1:],
                        [ (key, kwargs[key]) for key in sorted(kwargs.keys()) ]
)
)
).hexdigest()

def cache_this(key_getter, test_builder, timeout=10*60):
    def wrapped_decorator(func):
        def wrapped_func(*args, **kwargs):
            key = key_getter(func, *args, **kwargs)
            result = cache.get(key)
            if result is None:
                result = func(*args, **kwargs)
                cache.set(key, result, timeout)
                for model, test in test_builder(*args, **kwargs):
                    CACHE_DELETER.register_test(model, test, key)
            return result

        wrapped_func.__dict__ = func.__dict__
        wrapped_func.__doc__ = func.__doc__
        wrapped_func.__name__ = func.__name__

        return wrapped_func
    return wrapped_decorator

