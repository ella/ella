from django.core.cache import get_cache
from django.test import TestCase
from django.contrib.contenttypes.models import ContentType

from ella.core.cache import utils

from nose import tools, SkipTest

class TestCacheInvalidation(TestCase):
    def setUp(self):
        self.ct = ContentType.objects.get_for_model(ContentType)

        self.old_cache = utils.cache
        self.cache = get_cache('locmem://')
        utils.cache = self.cache
        super(TestCacheInvalidation, self).setUp()

    def tearDown(self):
        super(TestCacheInvalidation, self).tearDown()
        utils.cache = self.old_cache

    def test_save_invalidates_object(self):
        ct = utils.get_cached_object(self.ct, pk=self.ct.pk)

        tools.assert_equals(ct, self.ct)
        tools.assert_equals(self.ct, self.cache.get(utils._get_key(utils.KEY_PREFIX, self.ct, pk=self.ct.pk)))
        self.ct.save()
        tools.assert_equals(None, self.cache.get(utils._get_key(utils.KEY_PREFIX, self.ct, pkr=self.ct.pk)))

