# -*- coding: utf-8 -*-
from datetime import datetime
from djangosanetesting import DatabaseTestCase

from django.contrib.sites.models import Site

from ella.core.models import Placement, Category, Publishable
from ella.core.conf import core_settings
from django.core.management import call_command

from unit_project.test_core import create_basic_categories, create_and_place_a_publishable

class PublishableTestCase(DatabaseTestCase):
    def setUp(self):
        super(PublishableTestCase, self).setUp()
        create_basic_categories(self)
        create_and_place_a_publishable(self)

class TestPublishFrom(PublishableTestCase):
    def test_publish_from_is_set_to_placements(self):
        p = Publishable.objects.get(pk=self.publishable.pk)
        self.assert_equals(self.placement.publish_from, p.publish_from)

    def test_publish_from_is_reset_when_last_placement_deleted(self):
        self.placement.delete()
        self.assert_equals(core_settings.PUBLISH_FROM_WHEN_EMPTY, self.publishable.publish_from)

    def test_publish_from_is_updated_when_placement_moved_to_earlier(self):
        self.placement.publish_from = datetime(2000, 1, 1)
        self.placement.save()
        p = Publishable.objects.get(pk=self.publishable.pk)
        self.assert_equals(self.placement.publish_from, p.publish_from)

    def test_publish_from_is_updated_when_placement_postponed(self):
        self.placement.publish_from = datetime(2100, 1, 1)
        self.placement.save()
        p = Publishable.objects.get(pk=self.publishable.pk)
        self.assert_equals(self.placement.publish_from, p.publish_from)

    def test_with_more_placements_publish_from_is_the_earliest(self):
        p = Publishable.objects.get(pk=self.publishable.pk)
        Placement.objects.create(
            publishable=p,
            category=self.category,
            publish_from=datetime(2009,1,1)
        )

        p = Publishable.objects.get(pk=self.publishable.pk)
        self.assert_equals(self.placement.publish_from, p.publish_from)

    def test_publish_from_is_set_to_another_when_placement_deleted(self):
        Placement.objects.create(
            publishable=self.publishable,
            category=self.category,
            publish_from=datetime(2009,1,1)
        )
        self.placement.delete()
        self.assert_equals(datetime(2009,1,1), self.publishable.publish_from)

    def test_update_publishable_publish_from_sets_publish_from_properly(self):
        self.publishable.publish_from = datetime(2000, 1, 1)
        self.publishable.save()

        call_command('update_publishable_publish_from')
        p = Publishable.objects.get(pk=self.publishable.pk)
        self.assert_equals(self.placement.publish_from, p.publish_from)

    def test_update_publishable_publish_from_sets_publish_from_properly_with_no_placement(self):
        self.placement.delete()
        self.publishable.publish_from = datetime(2000, 1, 1)
        self.publishable.save()

        call_command('update_publishable_publish_from')
        p = Publishable.objects.get(pk=self.publishable.pk)
        self.assert_equals(core_settings.PUBLISH_FROM_WHEN_EMPTY, p.publish_from)


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

