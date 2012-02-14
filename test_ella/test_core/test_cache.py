from django.core.cache import get_cache
from django.test import TestCase
from django.contrib.contenttypes.models import ContentType

from ella.core.cache import utils

from nose import tools

class TestCacheInvalidation(TestCase):
    def setUp(self):
        self.ct = ContentType.objects.get_for_model(ContentType)
        local_cache.clear()
        super(TestCacheInvalidation, self).setUp()

    def test_save_invalidates_object(self):
        ct = utils.get_cached_object(self.ct, pk=self.ct.pk)

        tools.assert_equals(ct, self.ct)
        tools.assert_equals(self.ct, local_cache.get(utils._get_key(utils.KEY_PREFIX, self.ct, pk=self.ct.pk)))
        self.ct.save()
        tools.assert_equals(None, local_cache.get(utils._get_key(utils.KEY_PREFIX, self.ct, pkr=self.ct.pk)))


old_cache = None
local_cache = get_cache('locmem://')
def setup():
    global old_cache
    old_cache = utils.cache
    utils.cache = local_cache

def teardown():
    utils.cache = old_cache
