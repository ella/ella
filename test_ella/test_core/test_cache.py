from django.core.cache import get_cache
from django.conf import settings
from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import pre_save, post_save, post_delete

from ella.core.cache import utils, redis
from ella.core.models import Listing

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

class TestRedisListings(TestCase):
    def setUp(self):
        super(TestRedisListings, self).setUp()
        try:
            import redis as redis_client
        except ImportError:
            raise SkipTest()

        self.redis = redis_client.Redis(**settings.TEST_CORE_REDIS)

        redis.client = self.redis
        pre_save.connect(redis.listing_pre_save, sender=Listing)
        post_save.connect(redis.listing_post_save, sender=Listing)
        post_delete.connect(redis.listing_post_delete, sender=Listing)

    def tearDown(self):
        redis.client = None
        pre_save.disconnect(redis.listing_pre_save, sender=Listing)
        post_save.disconnect(redis.listing_post_save, sender=Listing)
        post_delete.disconnect(redis.listing_post_delete, sender=Listing)

        super(TestRedisListings, self).tearDown()
        self.redis.flushdb()

    def test_listing_save_adds_itself_to_relevant_zsets(self):
        raise SkipTest()

    def test_get_listing_uses_data_from_redis(self):
        raise SkipTest()
