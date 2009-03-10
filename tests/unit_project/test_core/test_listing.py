# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from djangosanetesting import DatabaseTestCase

from ella.core.models import Listing, Category

from unit_project.test_core import create_basic_categories, create_and_place_a_publishable, create_and_place_more_publishables

class TestListing(DatabaseTestCase):

    def setUp(self):
        super(TestListing, self).setUp()
        create_basic_categories(self)
        create_and_place_a_publishable(self)
        create_and_place_more_publishables(self)
        self.listing = Listing.objects.create(
                placement=self.placement,
                category=self.placement.category,
                publish_from=datetime.now() - timedelta(days=1),
            )

    def test_get_listing_empty(self):
        l = Listing.objects.get_listing(category=self.category)
        self.assert_equals(0, len(l))

    def test_get_listing_with_immediate_children(self):
        l = Listing.objects.get_listing(category=self.category, children=Listing.objects.IMMEDIATE)
        self.assert_equals(1, len(l))

    def test_get_listing_with_immediate_children_no_duplicates(self):
        listing = Listing.objects.create(
                placement=self.placement,
                category=self.category_nested_second,
                publish_from=datetime.now() - timedelta(days=2),
            )

        l = Listing.objects.get_listing(category=self.category_nested, children=Listing.objects.IMMEDIATE)
        self.assert_equals(1, len(l))
        self.assert_equals(self.listing, l[0])

    def test_get_listing_with_all_children_no_duplicates(self):
        listing = Listing.objects.create(
                placement=self.placement,
                category=self.category_nested_second,
                publish_from=datetime.now() - timedelta(days=2),
            )

        l = Listing.objects.get_listing(category=self.category, children=Listing.objects.ALL)
        self.assert_equals(1, len(l))
        self.assert_equals(self.listing, l[0])

    def test_get_listing_with_all_children(self):
        for p in self.placements:
            if p.category == self.category_nested_second:
                placement = p
                break

        listing = Listing.objects.create(
                placement=placement,
                category=placement.category,
                publish_from=datetime.now() - timedelta(days=2),
            )

        l = Listing.objects.get_listing(category=self.category, children=Listing.objects.ALL)
        self.assert_equals(2, len(l))
        self.assert_equals(self.listing, l[0])
        self.assert_equals(listing, l[1])

