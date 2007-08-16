import md5

from django.db.models import ObjectDoesNotExist
from django.core.cache import cache
from django.utils.encoding import smart_str
from django.http import Http404

from ella.core.cache.invalidate import CACHE_DELETER


KEY_FORMAT = 'alle.core.cache.utils.get_cached_object:%d:%s'
def get_cached_object(content_type, **kwargs):
    """
    Return a cached object. If the object does not exist in the cache, create it
    and register it for invalidation if the object is updated (check via _get_pk_val().

    Params:
        content_type - ContentType instance representing the model's class
        **kwargs - lookup parameters for content_type.get_object_for_this_type and for key creation

    Throws:
        model.DoesNotExist is propagated from content_type.get_object_for_this_type
    """
    key = md5.md5(KEY_FORMAT % (content_type.id, ':'.join('%s=%s' % (smart_str(key), smart_str(kwargs[key])) for key in sorted(kwargs.keys())))).hexdigest()

    obj = cache.get(key)
    if obj is None:
        obj = content_type.get_object_for_this_type(**kwargs)
        cache.set(key, obj)
        CACHE_DELETER.register(content_type.model_class(), lambda x: x._get_pk_val() == obj._get_pk_val(), key)
    return obj

def get_cached_object_or_404(content_type, **kwargs):
    """
    Shortcut that will raise Http404 if there is no object matching the query

    see get_cached_object for params description
    """
    try:
        return get_cached_object(content_type, **kwargs)
    except ObjectDoesNotExist:
        raise Http404

