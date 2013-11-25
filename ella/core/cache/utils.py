from hashlib import md5
import logging

from django.dispatch import receiver
from django.db.models import ObjectDoesNotExist
from django.db.models.loading import get_model
from django.db.models.signals import post_save, post_delete
from django.core.cache import cache
from django.core.cache.backends.dummy import DummyCache
from django.http import Http404
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import smart_str
from django.conf import settings


log = logging.getLogger('ella.core.cache.utils')

KEY_PREFIX = 'ella.obj'
CACHE_TIMEOUT = getattr(settings, 'CACHE_TIMEOUT', 10 * 60)


def invalidate_cache(sender, instance, **kwargs):
    invalidate_cache_for_object(instance)


def connect_invalidation_signals():
    post_save.connect(invalidate_cache)
    post_delete.connect(invalidate_cache)


def invalidate_cache_for_object(obj):
    key = _get_key(KEY_PREFIX, ContentType.objects.get_for_model(obj), pk=obj.pk, version_key=True)
    try:
        cache.incr(key)
    except ValueError:
        cache.set(key, 1, timeout=CACHE_TIMEOUT)


def normalize_key(key):
    if len(key) < 250:
        return key
    return md5(key).hexdigest()


def _get_key(start, model, pk=None, version_key=False, **kwargs):
    Publishable = get_model('core', 'publishable')
    if issubclass(model.model_class(), Publishable) and model.model_class() != Publishable:
        model = ContentType.objects.get_for_model(Publishable)

    if pk and not kwargs:
        key = ':'.join((
            start, str(model.pk), str(pk)
        ))
        if version_key:
            return key + ':VER'
        version = cache.get(key + ':VER') or '0'
        return '%s:%s' % (key, version)

    for key, val in kwargs.iteritems():
        if hasattr(val, 'pk'):
            kwargs[key] = val.pk

    return normalize_key(':'.join((
                start,
                str(model.pk),
                ','.join(':'.join((key, smart_str(kwargs[key]).replace(' ', '_'))) for key in sorted(kwargs.keys()))
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
        model_ct = ContentType.objects.get_for_model(model)
    else:
        model_ct = model

    key = _get_key(KEY_PREFIX, model_ct, **kwargs)

    obj = cache.get(key)
    if obj is None:
        # if we are looking for a publishable, fetch just the actual content
        # type and then fetch the actual object
        if model_ct.app_label == 'core' and model_ct.model == 'publishable':
            actual_ct_id = model_ct.model_class()._default_manager.values('content_type_id').get(**kwargs)['content_type_id']
            model_ct = ContentType.objects.get_for_id(actual_ct_id)

        # fetch the actual object we want
        obj = model_ct.model_class()._default_manager.get(**kwargs)

        # since 99% of lookups are done via PK make sure we set the cache for
        # that lookup even if we retrieved it using a different one.
        if 'pk' in kwargs:
            cache.set(key, obj, timeout)
        elif not isinstance(cache, DummyCache):
            cache.set_many({key: obj, _get_key(KEY_PREFIX, model_ct, pk=obj.pk): obj}, timeout=timeout)

    return obj


RAISE, SKIP, NONE = 0, 1, 2


def get_cached_objects(pks, model=None, timeout=CACHE_TIMEOUT, missing=RAISE):
    """
    Return a list of objects with given PKs using cache.

    Params:
        pks - list of Primary Key values to look up or list of content_type_id, pk tuples
        model - ContentType instance representing the model's class or the model class itself
        timeout - TTL for the items in cache, defaults to CACHE_TIMEOUT

    Throws:
        model.DoesNotExist is propagated from content_type.get_object_for_this_type
    """
    if model is not None:
        if not isinstance(model, ContentType):
            model = ContentType.objects.get_for_model(model)
        pks = [(model, pk) for pk in pks]
    else:
        pks = [(ContentType.objects.get_for_id(ct_id), pk) for (ct_id, pk) in pks]

    keys = [_get_key(KEY_PREFIX, model, pk=pk) for (model, pk) in pks]

    cached = cache.get_many(keys)

    # keys not in cache
    keys_to_set = set(keys) - set(cached.keys())
    if keys_to_set:
        # build lookup to get model and pks from the key
        lookup = dict(zip(keys, pks))

        to_get = {}
        # group lookups by CT so we can do in_bulk
        for k in keys_to_set:
            ct, pk = lookup[k]
            to_get.setdefault(ct, {})[int(pk)] = k

        # take out all the publishables
        publishable_ct = ContentType.objects.get_for_model(get_model('core', 'publishable'))
        if publishable_ct in to_get:
            publishable_keys = to_get.pop(publishable_ct)
            models = publishable_ct.model_class()._default_manager.values('content_type_id', 'id').filter(id__in=publishable_keys.keys())
            for m in models:
                ct = ContentType.objects.get_for_id(m['content_type_id'])
                pk = m['id']
                # and put them back as their native content_type
                to_get.setdefault(ct, {})[pk] = publishable_keys[pk]

        to_set = {}
        # retrieve all the models from DB
        for ct, vals in to_get.items():
            models = ct.model_class()._default_manager.in_bulk(vals.keys())
            for pk, m in models.items():
                k = vals[pk]
                cached[k] = to_set[k] = m

        if not isinstance(cache, DummyCache):
            # write them into cache
            cache.set_many(to_set, timeout=timeout)

    out = []
    for k in keys:
        try:
            out.append(cached[k])
        except KeyError:
            if missing == NONE:
                out.append(None)
            elif missing == SKIP:
                pass
            elif missing == RAISE:
                ct = ContentType.objects.get_for_id(int(k.split(':')[1]))
                raise ct.model_class().DoesNotExist(
                    '%s matching query does not exist.' % ct.model_class()._meta.object_name)
    return out


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

