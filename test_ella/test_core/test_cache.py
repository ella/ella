import time
from datetime import datetime

from django.core.cache import get_cache
from django.conf import settings
from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import pre_save, post_save, post_delete, pre_delete

from ella.core.cache import utils, redis
from ella.core.models import Listing
from ella.core.views import ListContentType
from ella.core.managers import ListingHandler
from ella.core.signals import content_published, content_unpublished

from test_ella.test_core import create_basic_categories, \
        create_and_place_more_publishables, list_all_publishables_in_category_by_hour

from nose import tools, SkipTest

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
        redis.connect_signals()

        create_basic_categories(self)
        create_and_place_more_publishables(self)

    def tearDown(self):
        redis.client = None
        pre_save.disconnect(redis.listing_pre_save, sender=Listing)
        post_save.disconnect(redis.listing_post_save, sender=Listing)
        pre_delete.disconnect(redis.listing_pre_delete, sender=Listing)
        post_delete.disconnect(redis.listing_post_delete, sender=Listing)
        content_published.disconnect(redis.publishable_published)
        content_unpublished.disconnect(redis.publishable_unpublished)

        super(TestRedisListings, self).tearDown()
        self.redis.flushdb()

    def test_listing_gets_removed_when_publishable_goes_unpublished(self):
        list_all_publishables_in_category_by_hour(self)
        p = self.publishables[0]
        p.published = False
        p.save()
        ct_id = p.content_type_id
        tools.assert_equals(set([
                'listing:2',
                'listing:3',

                'listing:c:1',
                'listing:c:2',
                'listing:c:3',

                'listing:d:1',
                'listing:d:2',
                'listing:d:3',

                'listing:ct:%d' % ct_id,
            ]),
            set(self.redis.keys())
        )
        tools.assert_equals(['%d:2' % ct_id, '%d:3' % ct_id], self.redis.zrange('listing:ct:%d' % ct_id, 0, 100))
        tools.assert_equals(['%d:2' % ct_id, '%d:3' % ct_id], self.redis.zrange('listing:d:1', 0, 100))
        tools.assert_equals(['%d:2' % ct_id], self.redis.zrange('listing:c:1', 0, 100))

    def test_listing_save_adds_itself_to_relevant_zsets(self):
        list_all_publishables_in_category_by_hour(self)
        ct_id = self.publishables[0].content_type_id
        tools.assert_equals(set([
                'listing:1',
                'listing:2',
                'listing:3',

                'listing:c:1',
                'listing:c:2',
                'listing:c:3',

                'listing:d:1',
                'listing:d:2',
                'listing:d:3',

                'listing:ct:%d' % ct_id,
            ]),
            set(self.redis.keys())
        )
        tools.assert_equals(['%d:3' % ct_id], self.redis.zrange('listing:3', 0, 100))
        tools.assert_equals(['%d:1' % ct_id, '%d:2' % ct_id, '%d:3' % ct_id], self.redis.zrange('listing:ct:%d' % ct_id, 0, 100))
        tools.assert_equals(['%d:1' % ct_id, '%d:2' % ct_id, '%d:3' % ct_id], self.redis.zrange('listing:d:1', 0, 100))

    def test_listing_delete_removes_itself_from_redis(self):
        list_all_publishables_in_category_by_hour(self)
        self.listings[1].delete()
        ct_id = self.publishables[0].content_type_id
        tools.assert_equals(set([
                'listing:1',
                'listing:3',

                'listing:c:1',
                'listing:c:2',
                'listing:c:3',

                'listing:d:1',
                'listing:d:2',
                'listing:d:3',

                'listing:ct:%d' % ct_id,
            ]),
            set(self.redis.keys())
        )
        tools.assert_equals(['%d:3' % ct_id], self.redis.zrange('listing:3', 0, 100))
        tools.assert_equals(['%d:3' % ct_id], self.redis.zrange('listing:c:2', 0, 100))
        tools.assert_equals(['%d:3' % ct_id], self.redis.zrange('listing:d:2', 0, 100))
        tools.assert_equals(['%d:1' % ct_id, '%d:3' % ct_id], self.redis.zrange('listing:d:1', 0, 100))
        tools.assert_equals(['%d:1' % ct_id], self.redis.zrange('listing:c:1', 0, 100))
        tools.assert_equals(['%d:1' % ct_id, '%d:3' % ct_id], self.redis.zrange('listing:ct:%d' % ct_id, 0, 100))

    def test_get_listing_uses_data_from_redis(self):
        ct_id = self.publishables[0].content_type_id
        t1, t2 = time.time()-90, time.time()-100
        self.redis.zadd('listing:c:2', '%d:1' % ct_id, repr(t1))
        self.redis.zadd('listing:c:2', '%d:3' % ct_id, repr(t2))
        dt1, dt2 = datetime.fromtimestamp(t1), datetime.fromtimestamp(t2)

        lh = Listing.objects.get_queryset_wrapper(category=self.category_nested, children=ListingHandler.IMMEDIATE, source='redis')
        tools.assert_equals(2, lh.count())
        l1, l2 = lh.get_listings(0, 10)

        tools.assert_equals(l1.publishable, self.publishables[0])
        tools.assert_equals(l2.publishable, self.publishables[2])
        tools.assert_equals(l1.publish_from, dt1)
        tools.assert_equals(l2.publish_from, dt2)

    def test_get_listing_omits_excluded_publishable(self):
        ct_id = self.publishables[0].content_type_id
        t1, t2 = time.time()-90, time.time()-100
        self.redis.zadd('listing:c:2', '%d:1' % ct_id, repr(t1))
        self.redis.zadd('listing:c:2', '%d:3' % ct_id, repr(t2))
        dt1, dt2 = datetime.fromtimestamp(t1), datetime.fromtimestamp(t2)

        lh = Listing.objects.get_queryset_wrapper(category=self.category_nested, children=ListingHandler.IMMEDIATE, exclude=self.publishables[0], source='redis')
        tools.assert_equals(1, lh.count())
        l = lh.get_listings(0, 10)

        tools.assert_equals(l[0].publishable, self.publishables[2])
        tools.assert_equals(l[0].publish_from, dt2)

    def test_redis_listing_handler_used_from_view_when_requested(self):
        ct_id = self.publishables[0].content_type_id
        t1, t2 = time.time()-90, time.time()-100
        self.redis.zadd('listing:d:2', '%d:1' % ct_id, repr(t1))
        self.redis.zadd('listing:d:2', '%d:3' % ct_id, repr(t2))
        dt1, dt2 = datetime.fromtimestamp(t1), datetime.fromtimestamp(t2)

        rf = RequestFactory()
        request = rf.get(self.category_nested.get_absolute_url(), {'using': 'redis'})
        lct = ListContentType()

        context = lct.get_context(request, self.category_nested.tree_path)
        tools.assert_equals(2, len(context['listings']))
        l1, l2 = context['listings']

        tools.assert_equals(l1.publishable, self.publishables[0])
        tools.assert_equals(l2.publishable, self.publishables[2])
        tools.assert_equals(l1.publish_from, dt1)
        tools.assert_equals(l2.publish_from, dt2)

    def test_get_listing_uses_data_from_redis_correctly_for_pagination(self):
        ct_id = self.publishables[0].content_type_id
        t1, t2, t3 = time.time()-90, time.time()-100, time.time() - 110
        self.redis.zadd('listing:c:2', '%d:1' % ct_id, repr(t1))
        self.redis.zadd('listing:c:2', '%d:3' % ct_id, repr(t2))
        self.redis.zadd('listing:c:2', '%d:2' % ct_id, repr(t3))

        lh = Listing.objects.get_queryset_wrapper(category=self.category_nested, children=ListingHandler.IMMEDIATE, source='redis')
        tools.assert_equals(3, lh.count())
        l = lh.get_listings(2, 1)

        tools.assert_equals(1, len(l))
        tools.assert_equals(l[0].publishable, self.publishables[1])
