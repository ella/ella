# -*- coding: utf-8 -*-
from djangosanetesting import DatabaseTestCase

from django.core.urlresolvers import reverse

from ella.core.models import Listing

from unit_project.test_core import create_basic_categories, create_and_place_a_publishable, \
        create_and_place_more_publishables, list_all_placements_in_category_by_hour

class TestFeeds(DatabaseTestCase):

    def setUp(self):
        try:
            import feedparser
        except ImportError, e:
            raise self.SkipTest()

        super(TestFeeds, self).setUp()
        create_basic_categories(self)
        create_and_place_a_publishable(self)
        create_and_place_more_publishables(self)
        list_all_placements_in_category_by_hour(self)

    def test_rss(self):
        import feedparser
        Listing.objects.all().update(category=self.category)
        url = reverse('feeds', kwargs={'url':'rss'})
        c = self.client

        response = c.get(url)
        self.assert_equals(200, response.status_code)
        d = feedparser.parse(response.content)

        self.assert_equals(len(self.placements), len(d['items']))

    def test_atom(self):
        import feedparser
        Listing.objects.all().update(category=self.category)
        url = reverse('feeds', kwargs={'url':'atom'})
        c = self.client

        response = c.get(url)
        self.assert_equals(200, response.status_code)
        d = feedparser.parse(response.content)

        self.assert_equals(len(self.placements), len(d['items']))




