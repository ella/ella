import time
from datetime import datetime

from django.core.cache import get_cache
from django.conf import settings
from django.test import TestCase
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import pre_save, post_save, post_delete

from ella.core.cache import utils, redis
from ella.core.models import Listing

from test_ella.test_core import create_basic_categories, \
        create_and_place_more_publishables, list_all_publishables_in_category_by_hour

from nose import tools, SkipTest

# Django 1.3 has a bug with Dummy cache where set_many doesn't accept timeout, "fix" it
utils.cache.__class__.set_many = lambda *a, **kw: None

class CacheTestCase(TestCase):
    def setUp(self):
        self.old_cache = utils.cache
        self.cache = get_cache('locmem://')
        utils.cache = self.cache
        super(CacheTestCase, self).setUp()

    def tearDown(self):
        super(CacheTestCase, self).tearDown()
        utils.cache = self.old_cache

class TestCacheUtils(CacheTestCase):
    def test_get_many_objects(self):
        ct_ct = ContentType.objects.get_for_model(ContentType)
        site_ct = ContentType.objects.get_for_model(Site)

        objs = utils.get_cached_objects([(ct_ct.id, ct_ct.id), (ct_ct.id, site_ct.id), (site_ct.id, 1)])

        tools.assert_equals([ct_ct, site_ct, Site.objects.get(pk=1)], objs)

class TestCacheInvalidation(CacheTestCase):
    def test_save_invalidates_object(self):
        self.ct = ContentType.objects.get_for_model(ContentType)
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

        create_basic_categories(self)
        create_and_place_more_publishables(self)

    def tearDown(self):
        redis.client = None
        pre_save.disconnect(redis.listing_pre_save, sender=Listing)
        post_save.disconnect(redis.listing_post_save, sender=Listing)
        post_delete.disconnect(redis.listing_post_delete, sender=Listing)

        super(TestRedisListings, self).tearDown()
        self.redis.flushdb()

    def test_listing_save_adds_itself_to_relevant_zsets(self):
        list_all_publishables_in_category_by_hour(self)
        ct_id = self.publishables[0].content_type_id
        tools.assert_equals(set([
                'listing:cat:1',
                'listing:cat:2',
                'listing:cat:3',
                'listing:ct:%d' % ct_id,
            ]),
            set(self.redis.keys())
        )
        tools.assert_equals(['17:3:0'], self.redis.zrange('listing:cat:3', 0, 100))
        tools.assert_equals(['17:1:0', '17:2:0', '17:3:0'], self.redis.zrange('listing:ct:%d' % ct_id, 0, 100))

    def test_get_listing_uses_data_from_redis(self):
        t1, t2 = time.time()-90, time.time()-100
        self.redis.zadd('listing:cat:3', '17:1:0', repr(t1))
        self.redis.zadd('listing:cat:2', '17:3:0', repr(t2))
        dt1, dt2 = datetime.fromtimestamp(t1), datetime.fromtimestamp(t2)

        lh = Listing.objects.get_queryset_wrapper(category=self.category_nested, children=Listing.objects.IMMEDIATE, source='redis')
        tools.assert_equals(2, lh.count())
        l1, l2 = lh.get_listings(0, 10)

        tools.assert_equals(l1.publishable, self.publishables[0])
        tools.assert_equals(l2.publishable, self.publishables[2])
        tools.assert_equals(l1.publish_from, dt1)
        tools.assert_equals(l2.publish_from, dt2)

