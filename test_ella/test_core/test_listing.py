# -*- coding: utf-8 -*-
from datetime import timedelta

from test_ella.cases import RedisTestCase as TestCase

from nose import tools

from ella.core.cache.redis import RedisListingHandler, TimeBasedListingHandler
from ella.core.models import Listing, Category
from ella.core.managers import ListingHandler
from ella.utils.timezone import now

from test_ella.test_core import create_basic_categories, create_and_place_a_publishable, \
        create_and_place_more_publishables, list_all_publishables_in_category_by_hour

class TestListing(TestCase):

    def setUp(self):
        super(TestListing, self).setUp()
        create_basic_categories(self)
        create_and_place_a_publishable(self)
        create_and_place_more_publishables(self)
        list_all_publishables_in_category_by_hour(self)

    def test_nested_listings(self):
        list_all_publishables_in_category_by_hour(self, category=self.category_nested_second)
        list_all_publishables_in_category_by_hour(self, category=self.category_nested)
        l = Listing.objects.get_listing(category=self.category_nested, children=ListingHandler.ALL)
        tools.assert_equals(self.listings, list(l))

    def test_get_listing_empty(self):
        c = Category.objects.create(
            title=u"third nested category",
            description=u"category nested in case.category_nested_second",
            tree_parent=self.category_nested_second,
            site_id = self.site_id,
            slug=u"third-nested-category",
        )

        l = Listing.objects.get_listing(category=c)
        tools.assert_equals(0, len(l))

    def test_get_listing_with_immediate_children(self):
        l = Listing.objects.get_listing(category=self.category, children=ListingHandler.IMMEDIATE)
        expected = [listing for listing in self.listings if listing.category in (self.category, self.category_nested)]
        tools.assert_equals(expected, l)

    def test_listing_only_contains_published_items(self):
        potential = [listing for listing in self.listings if listing.category in (self.category, self.category_nested)]
        actual = potential.pop()
        expected = [actual]
        for l in potential:
            if l.publishable != actual.publishable:
                l.publishable.published = False
                l.publishable.save()
            else:
                expected.append(l)
        l = Listing.objects.get_listing(category=self.category, children=ListingHandler.IMMEDIATE)
        tools.assert_equals(expected, l)


    def test_get_listing_with_immediate_children_no_duplicates(self):
        expected = [listing for listing in self.listings if listing.category in (self.category, self.category_nested)]

        listing = Listing.objects.create(
                publishable=expected[0].publishable,
                category=expected[0].category,
                publish_from=now() - timedelta(days=2),
            )
        expected[0] = listing
        l = Listing.objects.get_listing(category=self.category, children=ListingHandler.IMMEDIATE)
        tools.assert_equals(expected, l)

    def test_get_listing_with_all_children_no_duplicates(self):
        listing = Listing.objects.create(
                publishable=self.publishables[0],
                category=self.category_nested_second,
                publish_from=now() - timedelta(days=2),
            )

        l = Listing.objects.get_listing(category=self.category, children=ListingHandler.ALL)
        tools.assert_equals(len(self.listings), len(l))
        tools.assert_equals(listing, l[0])

    def test_get_listing_IMMEDIATE_without_limited_categories(self):
        self.category_nested.app_data = {'ella': {'propagate_listings': False}}
        self.category_nested.save()
        l = Listing.objects.get_listing(category=self.category, children=ListingHandler.IMMEDIATE)
        tools.assert_equals(1, len(l))
        tools.assert_equals([listing for listing in self.listings if listing.category == self.category], l)

    def test_get_listing_ALL_without_limited_categories(self):
        self.category_nested.app_data = {'ella': {'propagate_listings': False}}
        self.category_nested.save()
        l = Listing.objects.get_listing(category=self.category, children=ListingHandler.ALL)
        tools.assert_equals(1, len(l))
        tools.assert_equals([listing for listing in self.listings if listing.category == self.category], l)

    def test_get_listing_with_all_children(self):
        l = Listing.objects.get_listing(category=self.category, children=ListingHandler.ALL)
        tools.assert_equals(self.listings, list(l))

    def test_inactive_istings_wont_show(self):
        l = self.listings[0]
        l.publish_to = now() - timedelta(days=1)
        l.save()

        l = Listing.objects.get_listing(category=self.category, children=ListingHandler.ALL)

        tools.assert_equals(self.listings[1:], l)

    def test_excluded_publishable_wont_show(self):
        l = self.listings[0]
        l = Listing.objects.get_listing(category=self.category, children=ListingHandler.ALL, exclude=l.publishable)
        tools.assert_equals(self.listings[1:], l)

    def test_queryset_wrapper_can_get_individual_listings(self):
        lh = Listing.objects.get_queryset_wrapper(self.category, children=ListingHandler.ALL)
        l = lh[0]
        tools.assert_equals(self.listings[0], l)


class TestRedisListingHandler(TestCase):
    " Unit tests for the RedisListingHandler. "
    def setUp(self):
        super(TestRedisListingHandler, self).setUp()
        create_basic_categories(self)
        create_and_place_a_publishable(self)
        create_and_place_more_publishables(self)
        list_all_publishables_in_category_by_hour(self)

    def test_get_listings(self):
        " Assert that `get_listings` returns the appropriate data. "
        # Instantiate the RedisListingHandler and have it fetch all children
        lh = RedisListingHandler(self.category, ListingHandler.ALL)
        all_listings = lh.get_listings()
        tools.assert_equals(len(all_listings), len(self.listings))

        # Assert that the offset and count are returning the correct data
        # Fetch 10 results - only 3 listings
        partial = lh.get_listings(offset=0, count=10)
        tools.assert_equals(len(partial), 3)
        tools.assert_equals(
            [l.publishable for l in partial],
            [l.publishable for l in self.listings]
        )

        # Only fetch the first result
        partial = lh.get_listings(offset=0, count=1)
        tools.assert_equals(len(partial), 1)
        tools.assert_equals(
            [l.publishable for l in partial],
            [self.listings[0].publishable]
        )

        # Fetch the first 2 results results
        partial = lh.get_listings(offset=0, count=2)
        tools.assert_equals(len(partial), 2)
        tools.assert_equals(
            [l.publishable for l in partial],
            [l.publishable for l in self.listings[0:2]]
        )

        # Fetch 2 results offset by 1
        partial = lh.get_listings(offset=1, count=2)
        tools.assert_equals(len(partial), 2)
        tools.assert_equals(
            [l.publishable for l in partial],
            [l.publishable for l in self.listings[1:3]]
        )

        # Fetch 3 offset by 2, only 1 returned
        partial = lh.get_listings(offset=2, count=3)
        tools.assert_equals(len(partial), 1)
        tools.assert_equals(
            [l.publishable for l in partial],
            [self.listings[2].publishable]
        )

        # Fetch 3 offset by 3 - returns 0
        partial = lh.get_listings(offset=3, count=3)
        tools.assert_equals(len(partial), 0)

        # Essentially no limit (fetch all)
        partial = lh.get_listings(offset=0, count=0)
        tools.assert_equals(len(partial), 3)
        tools.assert_equals(
            [l.publishable for l in partial],
            [l.publishable for l in self.listings]
        )

class TestTimeBasedListingHandler(TestRedisListingHandler):
    " Unit tests for the TimeBasedListingHandler."
    def test_get_listings(self):
        " Assert that `get_listings` returns the appropriate data. "
        # Instantiate the RedisListingHandler and have it fetch all children
        lh = TimeBasedListingHandler(self.category, ListingHandler.ALL)
        all_listings = lh.get_listings()
        tools.assert_equals(len(all_listings), len(self.listings))

        # Assert that the offset and count are returning the correct data
        # Fetch 10 results - only 3 listings
        partial = lh.get_listings(offset=0, count=10)
        tools.assert_equals(len(partial), 3)
        tools.assert_equals(
            [l.publishable for l in partial],
            [l.publishable for l in self.listings]
        )

        # Only fetch the first result
        partial = lh.get_listings(offset=0, count=1)
        tools.assert_equals(len(partial), 1)
        tools.assert_equals(
            [l.publishable for l in partial],
            [self.listings[0].publishable]
        )

        # Fetch the first 2 results results
        partial = lh.get_listings(offset=0, count=2)
        tools.assert_equals(len(partial), 2)
        tools.assert_equals(
            [l.publishable for l in partial],
            [l.publishable for l in self.listings[0:2]]
        )

        # Fetch 2 results offset by 1
        partial = lh.get_listings(offset=1, count=2)
        tools.assert_equals(len(partial), 2)
        tools.assert_equals(
            [l.publishable for l in partial],
            [l.publishable for l in self.listings[1:3]]
        )

        # Fetch 3 offset by 2, only 1 returned
        partial = lh.get_listings(offset=2, count=3)
        tools.assert_equals(len(partial), 1)
        tools.assert_equals(
            [l.publishable for l in partial],
            [self.listings[2].publishable]
        )
