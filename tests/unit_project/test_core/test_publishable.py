# -*- coding: utf-8 -*-
from datetime import datetime
from djangosanetesting import DatabaseTestCase

from django.contrib.sites.models import Site

from ella.core.models import Placement, Category

from unit_project.test_core import create_basic_categories, create_and_place_a_publishable

class TestPublishable(DatabaseTestCase):

    def setUp(self):
        super(TestPublishable, self).setUp()
        create_basic_categories(self)
        create_and_place_a_publishable(self)

    def test_url(self):
        self.assert_equals('/nested-category/2008/1/10/articles/first-article/', self.publishable.get_absolute_url())

    def test_domain_url(self):
        self.assert_equals('http://example.com/nested-category/2008/1/10/articles/first-article/', self.publishable.get_domain_url())

    def test_main_placement_with_single_placement(self):
        self.assert_equals(self.placement, self.publishable.main_placement)

    def test_main_placement_with_single_placement_on_other_site(self):
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

    def test_main_placement_with_two_placements_on_one_site(self):
        Placement.objects.create(
            target_ct=self.publishable_ct,
            target_id=self.publishable.pk,
            category=self.category,
            publish_from=datetime(2008,1,10)
        )
        self.assert_equals(self.placement, self.publishable.main_placement)

    def test_main_placement_with_two_placements_on_two_sites(self):
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
            target_ct=self.publishable_ct,
            target_id=self.publishable.pk,
            category=category,
            publish_from=datetime(2008,1,10)
        )

        self.assert_equals(self.placement, self.publishable.main_placement)

