from django.test import TestCase

invalidation = r'''
>>> import time
>>> from django.core.cache import cache
>>> from ella.core.cache import invalidate
>>> from coretest.cache_tests.models import CachedModel
>>> cm = CachedModel.objects.get(pk=1)
>>> key = 'CachedModel:%d' % cm.id
>>> cache.set(key, cm)
>>> invalidate.CACHE_DELETER.register_pk(cm, key)
>>> invalidate.CACHE_DELETER.register_test(CachedModel, 'id:1', key)
>>> cm == cache.get(key)
True
>>> cm.title = 'some other title'
>>> cm.save()
>>> time.sleep(2)
>>> cache.get(key) is None
True
'''

get_object = r'''
>>> import time
>>> from ella.core.cache import get_cached_object
>>> from django.contrib.contenttypes.models import ContentType
>>> from coretest.cache_tests.models import CachedModel
>>> ct = ContentType.objects.get_for_model(CachedModel)
>>> cm = get_cached_object(ct, pk=1)
>>> cm.id
1
>>> cm.title[:4]
u'some'
>>> cm.title = 'XXX'
>>> cm.save()
>>> time.sleep(2)
>>> cm2 = get_cached_object(ct, pk=1)
>>> cm2.title
u'XXX'
'''

__test__ = {
    'invalidation' : invalidation,
    'get_object' : get_object,
}

if __name__ == '__main__':
    import doctest
    doctest.testmod()

