# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from djangosanetesting import DatabaseTestCase

from ella.core.models import Listing, Category

from unit_project.test_core import create_basic_categories, create_and_place_a_publishable, \
        create_and_place_more_publishables, list_all_placements_in_category_by_hour

class TestListing(DatabaseTestCase):

    def setUp(self):
        super(TestListing, self).setUp()
        create_basic_categories(self)
        create_and_place_a_publishable(self)
        create_and_place_more_publishables(self)
        list_all_placements_in_category_by_hour(self)

    def test_get_listing_empty(self):
        c = Category.objects.create(
            title=u"third nested category",
            description=u"category nested in case.category_nested_second",
            tree_parent=self.category_nested_second,
            site_id = self.site_id,
            slug=u"third-nested-category",
        )

        l = Listing.objects.get_listing(category=c)
        self.assert_equals(0, len(l))

    def test_get_listing_with_immediate_children(self):
        l = Listing.objects.get_listing(category=self.category, children=Listing.objects.IMMEDIATE)
        expected = [listing for listing in self.listings if listing.category in (self.category, self.category_nested)]
        self.assert_equals(expected, l)

    def test_get_listing_with_immediate_children_no_duplicates(self):
        expected = [listing for listing in self.listings if listing.category in (self.category, self.category_nested)]

        listing = Listing.objects.create(
                placement=expected[0].placement,
                category=expected[0].category,
                publish_from=datetime.now() - timedelta(days=2),
            )
        expected[0] = listing
        l = Listing.objects.get_listing(category=self.category, children=Listing.objects.IMMEDIATE)
        self.assert_equals(expected, l)

    def test_get_listing_with_all_children_no_duplicates(self):
        listing = Listing.objects.create(
                placement=self.placements[0],
                category=self.category_nested_second,
                publish_from=datetime.now() - timedelta(days=2),
            )

        l = Listing.objects.get_listing(category=self.category, children=Listing.objects.ALL)
        self.assert_equals(len(self.listings), len(l))
        self.assert_equals(listing, l[0])

    def test_get_listing_with_all_children(self):
        l = Listing.objects.get_listing(category=self.category, children=Listing.objects.ALL)
        self.assert_equals(self.listings, l)

    def test_inactive_istings_wont_show(self):
        l = self.listings[0]
        l.publish_to = datetime.now() - timedelta(days=1)
        l.save()

        l = Listing.objects.get_listing(category=self.category, children=Listing.objects.ALL)

        self.assert_equals(self.listings[1:], l)

    def test_prioritized_listing_will_be_first(self):
        l = self.listings[-1]
        l.priority_value = 10
        l.priority_from = datetime.now() - timedelta(days=1)
        l.priority_to = datetime.now() + timedelta(days=1)
        l.save()

        expected = [l] + self.listings[:-1]

        l = Listing.objects.get_listing(category=self.category, children=Listing.objects.ALL)

        self.assert_equals(expected, l)

    def test_de_prioritized_listing_will_be_last(self):
        l = self.listings[0]
        l.priority_value = -10
        l.priority_from = datetime.now() - timedelta(days=1)
        l.priority_to = datetime.now() + timedelta(days=1)
        l.save()

        expected = self.listings[1:] + [l]

        l = Listing.objects.get_listing(category=self.category, children=Listing.objects.ALL)

        self.assert_equals(expected, l)


    def test_inactive_priority_wont_affect_things(self):
        l = self.listings[0]
        l.priority_value = -10
        l.priority_from = datetime.now() - timedelta(days=2)
        l.priority_to = datetime.now() - timedelta(days=1)
        l.save()

        l = Listing.objects.get_listing(category=self.category, children=Listing.objects.ALL)

        self.assert_equals(self.listings, l)

    def test_count_works_accross_priorities(self):
        l = self.listings[-1]
        l.priority_value = 10
        l.priority_from = datetime.now() - timedelta(days=1)
        l.priority_to = datetime.now() + timedelta(days=1)
        l.save()

        expected = [l, self.listings[0]]

        l = Listing.objects.get_listing(category=self.category, children=Listing.objects.ALL, offset=1, count=2)

        self.assert_equals(expected, l)

    def test_offset_and_count_works_accross_priorities(self):
        l = self.listings[-1]
        for l in self.listings[-2:]:
            l.priority_value = 10
            l.priority_from = datetime.now() - timedelta(days=1)
            l.priority_to = datetime.now() + timedelta(days=1)
            l.save()

        expected = [l, self.listings[0]]

        l = Listing.objects.get_listing(category=self.category, children=Listing.objects.ALL, offset=2, count=2)

        self.assert_equals(expected, l)
