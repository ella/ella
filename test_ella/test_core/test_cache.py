import time
from datetime import date

from django.core.cache import get_cache
from ella.core.cache.redis import DEFAULT_REDIS_HANDLER
from ella.core.cache.utils import normalize_key
from hashlib import md5
from django.conf import settings
from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import pre_save, post_save, post_delete, pre_delete

from ella.core.cache import utils, redis
from ella.core.models import Listing, Publishable
from ella.core.views import ListContentType
from ella.core.managers import ListingHandler
from ella.core.signals import content_published, content_unpublished
from ella.articles.models import Article
from ella.utils.timezone import from_timestamp

from test_ella.test_core import create_basic_categories, create_and_place_a_publishable, \
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

    def test_get_many_publishables_will_respect_their_content_type(self):
        create_basic_categories(self)
        create_and_place_a_publishable(self)
        objs = utils.get_cached_objects([self.publishable.pk], Publishable)

        tools.assert_true(isinstance(objs[0], Article))

    def test_get_many_objects_raises_by_default(self):
        ct_ct = ContentType.objects.get_for_model(ContentType)
        site_ct = ContentType.objects.get_for_model(Site)

        tools.assert_raises(Site.DoesNotExist, utils.get_cached_objects, [(ct_ct.id, ct_ct.id), (ct_ct.id, site_ct.id), (site_ct.id, 1), (site_ct.id, 100)])

    def test_get_many_objects_can_replace_missing_with_none(self):
        ct_ct = ContentType.objects.get_for_model(ContentType)
        site_ct = ContentType.objects.get_for_model(Site)

        objs = utils.get_cached_objects([(ct_ct.id, ct_ct.id), (ct_ct.id, site_ct.id), (site_ct.id, 1), (site_ct.id, 100)], missing=utils.NONE)
        tools.assert_equals([ct_ct, site_ct, Site.objects.get(pk=1), None], objs)

    def test_get_many_objects_can_skip(self):
        ct_ct = ContentType.objects.get_for_model(ContentType)
        site_ct = ContentType.objects.get_for_model(Site)

        objs = utils.get_cached_objects([(ct_ct.id, ct_ct.id), (ct_ct.id, site_ct.id), (site_ct.id, 1), (site_ct.id, 100)], missing=utils.SKIP)
        tools.assert_equals([ct_ct, site_ct, Site.objects.get(pk=1)], objs)

    def test_get_publishable_returns_subclass(self):
        create_basic_categories(self)
        create_and_place_a_publishable(self)

        tools.assert_equals(self.publishable, utils.get_cached_object(Publishable, pk=self.publishable.pk))

    def test_get_article_uses_the_publishable_key(self):
        tools.assert_equals(
            ':'.join((utils.KEY_PREFIX, str(ContentType.objects.get_for_model(Publishable).pk), '123')),
            utils._get_key(utils.KEY_PREFIX, ContentType.objects.get_for_model(Article), pk=123)
        )

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

    def test_access_to_individual_listings(self):
        list_all_publishables_in_category_by_hour(self)
        lh = Listing.objects.get_queryset_wrapper(category=self.category, children=ListingHandler.ALL, source='redis')
        l = lh[0]

        tools.assert_equals(l.publishable, self.listings[0].publishable)

    def test_listings_dont_propagate_where_they_shouldnt(self):
        self.category_nested.app_data = {'ella': {'propagate_listings': False}}
        self.category_nested.save()

        # small hack to remove the cached category on Publishable
        for p in self.publishables:
            del p._category_cache

        list_all_publishables_in_category_by_hour(self)
        ct_id = self.publishables[0].content_type_id
        tools.assert_equals(['%d:1' % ct_id], self.redis.zrange('listing:d:1', 0, 100))
        tools.assert_equals(['%d:1' % ct_id], self.redis.zrange('listing:c:1', 0, 100))
        tools.assert_equals(['%d:2' % ct_id, '%d:3' % ct_id], self.redis.zrange('listing:c:2', 0, 100))
        tools.assert_equals(['%d:2' % ct_id, '%d:3' % ct_id], self.redis.zrange('listing:d:2', 0, 100))

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
        dt1, dt2 = from_timestamp(t1), from_timestamp(t2)

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
        dt1, dt2 = from_timestamp(t1), from_timestamp(t2)

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
        dt1, dt2 = from_timestamp(t1), from_timestamp(t2)

        rf = RequestFactory()
        request = rf.get(self.category_nested.get_absolute_url(), {'using': 'redis'})
        lct = ListContentType()

        context = lct.get_context(request, self.category_nested)
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


class TestAuthorLH(TestCase):
    def setUp(self):
        from ella.core.models import Author

        super(TestAuthorLH, self).setUp()

        try:
            import redis as redis_client
        except ImportError:
            raise SkipTest()

        self.redis = redis_client.Redis(**settings.TEST_CORE_REDIS)

        redis.client = self.redis
        redis.connect_signals()

        create_basic_categories(self)
        create_and_place_more_publishables(self)

        self.author = Author.objects.create(slug='testauthor')

        settings.LISTING_HANDLERS[DEFAULT_REDIS_HANDLER] = 'ella.core.cache.redis.AuthorListingHandler'

        for p in self.publishables:
            p.authors = [self.author]
            p.save()


    def tearDown(self):
        redis.client = None
        pre_save.disconnect(redis.listing_pre_save, sender=Listing)
        post_save.disconnect(redis.listing_post_save, sender=Listing)
        pre_delete.disconnect(redis.listing_pre_delete, sender=Listing)
        post_delete.disconnect(redis.listing_post_delete, sender=Listing)
        content_published.disconnect(redis.publishable_published)
        content_unpublished.disconnect(redis.publishable_unpublished)

        super(TestAuthorLH, self).tearDown()
        self.redis.flushdb()


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

            'listing:a:%d' % self.author.pk,

            'listing:ct:%d' % ct_id,

            ]),
            set(self.redis.keys())
        )
        tools.assert_equals(['%d:1' % ct_id, '%d:2' % ct_id, '%d:3' % ct_id],
                            self.redis.zrange('listing:a:1', 0, 100))


class SlidingLH(redis.SlidingListingHandler):
    PREFIX = 'sliding'


class TestSlidingListings(TestCase):
    def setUp(self):
        super(TestSlidingListings, self).setUp()
        try:
            import redis as redis_client
        except ImportError:
            raise SkipTest()

        self.redis = redis_client.Redis(**settings.TEST_CORE_REDIS)

        redis.client = self.redis

        create_basic_categories(self)
        create_and_place_more_publishables(self)
        self.ct_id = self.publishables[0].content_type_id

    def tearDown(self):
        redis.client = None
        super(TestSlidingListings, self).tearDown()
        self.redis.flushdb()

    def test_add_publishable_pushes_to_day_and_global_keys(self):
        SlidingLH.add_publishable(self.category, self.publishables[0], 10)
        day = date.today().strftime('%Y%m%d')
        expected_base = [
            'sliding:1',
            'sliding:c:1',
            'sliding:d:1',
            'sliding:ct:%s' % self.ct_id,
        ]
        expected = expected_base + [k + ':' + day for k in expected_base] + ['sliding:KEYS', 'sliding:WINDOWS']
        tools.assert_equals(set(expected), set(self.redis.keys(SlidingLH.PREFIX + '*')))
        tools.assert_equals(self.redis.zrange('sliding:d:1', 0, -1, withscores=True), self.redis.zrange('sliding:d:1' + ':' + day, 0, -1, withscores=True))

    def test_slide_windows_regenerates_aggregates(self):
        SlidingLH.add_publishable(self.category, self.publishables[0], 10)
        # register the keys that should exist
        self.redis.sadd('sliding:KEYS', 'sliding:1', 'sliding:c:1')

        self.redis.zadd('sliding:1:20101010', **{'17:1': 10, '17:2': 1})
        self.redis.zadd('sliding:1:20101009', **{'17:1': 9, '17:2': 2})
        self.redis.zadd('sliding:1:20101007', **{'17:1': 8, '17:2': 3, '17:3': 11})
        self.redis.zadd('sliding:1:20101001', **{'17:1': 8, '17:2': 3, '17:3': 11})


        SlidingLH.regenerate(date(2010, 10, 10))
        tools.assert_equals([('17:2', 6.0), ('17:3', 11.0), ('17:1', 27.0)], self.redis.zrange('sliding:1', 0, -1, withscores=True))

    def test_regenerate_removes_old_slots(self):
        self.redis.zadd('sliding:WINDOWS', **{
                'sliding:1:20101010': 20101010,
                'sliding:1:20101009': 20101009,
                'sliding:1:20101007': 20101007,
                'sliding:1:20101001': 20101001
            })
        self.redis.zadd('sliding:1:20101010', **{'17:1': 10, '17:2': 1})
        self.redis.zadd('sliding:1:20101009', **{'17:1': 9, '17:2': 2})
        self.redis.zadd('sliding:1:20101007', **{'17:1': 8, '17:2': 3, '17:3': 11})
        self.redis.zadd('sliding:1:20101001', **{'17:1': 8, '17:2': 3, '17:3': 11})

        SlidingLH.regenerate(date(2010, 10, 10))
        tools.assert_false(self.redis.exists('sliding:1:20101001'))
        tools.assert_true(self.redis.exists('sliding:1:20101007'))
        tools.assert_equals([
                ('sliding:1:20101007', 20101007),
                ('sliding:1:20101009', 20101009),
                ('sliding:1:20101010', 20101010)
            ],
            self.redis.zrange('sliding:WINDOWS', 0, -1, withscores=True)
        )
def test_normalize_key_doesnt_touch_short_key():
    key = "thisistest"
    tools.assert_equals(key,normalize_key(key))

def test_normalize_key_md5s_long_key():
    key = "0123456789" * 30
    tools.assert_equals(md5(key).hexdigest(),normalize_key(key))

