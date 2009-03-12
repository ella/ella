# -*- coding: utf-8 -*-
from datetime import datetime
from djangosanetesting import DatabaseTestCase

from django.contrib.sites.models import Site

from ella.core.models import Placement, Category

from unit_project.test_core import create_basic_categories, create_and_place_a_publishable

class PublishableTestCase(DatabaseTestCase):
    def setUp(self):
        super(PublishableTestCase, self).setUp()
        create_basic_categories(self)
        create_and_place_a_publishable(self)

class TestPublishableHelpers(PublishableTestCase):

    def test_url(self):
        self.assert_equals('/nested-category/2008/1/10/articles/first-article/', self.publishable.get_absolute_url())

    def test_domain_url(self):
        self.assert_equals('http://example.com/nested-category/2008/1/10/articles/first-article/', self.publishable.get_domain_url())


class TestMainPlacement(PublishableTestCase):

    def test_single_placement(self):
        self.assert_equals(self.placement, self.publishable.main_placement)

    def test_single_placement_on_other_site(self):
        site = Site.objects.create(
            name='some site',
            domain='not-example.com'
        )

        category = Category.objects.create(
            title=u"再见 category",
            description=u"example testing category, second site",
            site=site,
            slug=u'zai-jian-category',
        )

        self.placement.category = category
        self.placement.save()
        
        self.assert_equals(None, self.publishable.main_placement)

    def test_with_more_placements_one_with_first_publish_from_is_main(self):
        Placement.objects.create(
            publishable=self.publishable,
            category=self.category,
            publish_from=datetime(2008,1,11)
        )

        self.assert_equals(self.placement, self.publishable.main_placement)

    def test_with_more_placements_one_with_first_publish_from_is_main_even_when_added_as_second(self):
        placement_old = Placement.objects.create(
            publishable=self.publishable,
            category=self.category,
            publish_from=datetime(2007, 1, 10)
        )

        self.assert_equals(placement_old, self.publishable.main_placement)

    def test_two_placements_on_two_sites(self):
        site = Site.objects.create(
            name='some site',
            domain='not-example.com'
        )

        category = Category.objects.create(
            title=u"再见 category",
            description=u"example testing category, second site",
            site=site,
            slug=u'zai-jian-category',
        )
        
        Placement.objects.create(
            publishable=self.publishable,
            category=category,
            publish_from=datetime(2008,1,10)
        )

        self.assert_equals(self.placement, self.publishable.main_placement)

