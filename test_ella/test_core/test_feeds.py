# -*- coding: utf-8 -*-
from test_ella.cases import RedisTestCase as TestCase

from nose import tools, SkipTest

from django.core.urlresolvers import reverse
from django.template import Context

from ella.core.models import Listing
from ella.core.feeds import RSSTopCategoryListings
from ella.photos.models import Format

from test_ella.test_core import create_basic_categories, \
        create_and_place_more_publishables, list_all_publishables_in_category_by_hour
from test_ella import template_loader

class TestFeeds(TestCase):

    def setUp(self):
        try:
            import feedparser
        except ImportError:
            raise SkipTest()

        super(TestFeeds, self).setUp()
        create_basic_categories(self)
        create_and_place_more_publishables(self)
        list_all_publishables_in_category_by_hour(self)


        self._feeder = RSSTopCategoryListings()

    def tearDown(self):
        super(TestFeeds, self).tearDown()
        template_loader.templates.clear()

    def _set_photo(self):
        from test_ella.test_photos.fixtures import create_photo

        photo = create_photo(self)

        self.publishables[0].photo = photo
        self.publishables[0].save()
        # update the cache on the Listing object
        self.listings[0].publishable = self.publishables[0]

    def test_rss(self):
        import feedparser
        Listing.objects.all().update(category=self.category)
        url = reverse('home_rss_feed')
        c = self.client

        response = c.get(url)
        tools.assert_equals(200, response.status_code)
        d = feedparser.parse(response.content)

        tools.assert_equals(len(self.publishables), len(d['items']))

    def test_guids_set_properly_in_rss(self):
        import feedparser
        Listing.objects.all().update(category=self.category)
        url = reverse('home_atom_feed')
        c = self.client

        response = c.get(url)
        tools.assert_equals(200, response.status_code)
        d = feedparser.parse(response.content)

        tools.assert_equals(len(d['items']), len(set(i['guid'] for i in d['items'])))

    def test_atom(self):
        import feedparser
        Listing.objects.all().update(category=self.category)
        url = reverse('home_atom_feed')
        c = self.client

        response = c.get(url)
        tools.assert_equals(200, response.status_code)
        d = feedparser.parse(response.content)

        tools.assert_equals(len(self.publishables), len(d['items']))

    def test_title_defaults_to_category_title(self):
        tools.assert_true(self._feeder.title(self.category), self.category.title)

    def test_title_uses_app_data_when_set(self):
        self.category.app_data = {'syndication': {'title': 'SYNDICATION_TITLE'}}
        tools.assert_true(self._feeder.title(self.category), 'SYNDICATION_TITLE')

    def test_description_defaults_to_category_title(self):
        tools.assert_true(self._feeder.title(self.category), self.category.title)

    def test_description_uses_app_data_when_set(self):
        self.category.app_data = {'syndication': {'description': 'SYNDICATION_DESCRIPTION'}}
        tools.assert_true(self._feeder.description(self.category), 'SYNDICATION_DESCRIPTION')

    def test_no_enclosure_when_format_not_set(self):
        feeder = RSSTopCategoryListings()
        feeder.format = None
        self._set_photo()
        tools.assert_true(self.publishables[0].photo is not None)
        tools.assert_equals(None, feeder.item_enclosure_url(self.listings[0]))

    def test_get_enclosure_uses_optional_hook_on_publishable(self):
        class A(object):
            @property
            def publishable(self):
                return self

            def feed_enclosure(self):
                return {'url': 'URL', 'size': 1000}

        tools.assert_equals('URL', self._feeder.item_enclosure_url(A()))
        tools.assert_equals(1000, self._feeder.item_enclosure_length(A()))

    def test_get_enclosure_uses_formated_photo_when_format_available(self):
        f = Format.objects.create(name='enc_format', max_width=10, max_height=10,
            flexible_height=False, stretch=False, nocrop=False)

        feeder = RSSTopCategoryListings()
        feeder.format = f

        self._set_photo()
        tools.assert_true(self.publishables[0].photo is not None)
        original = self.publishables[0].photo.image
        new = self._feeder.item_enclosure_url(self.listings[0])
        tools.assert_not_equals(unicode(original), unicode(new))

    def test_get_enclosure_returns_none_when_no_image_set(self):
        tools.assert_equals(self._feeder.item_enclosure_url(self.listings[0]), None)

    def test_item_description_defaults_to_publishable_description(self):
        feeder = RSSTopCategoryListings()
        feeder.box_context = {}
        tools.assert_equals(self.publishables[-1].description, feeder.item_description(self.listings[0]))

    def test_box_rss_description_can_override_rss_description(self):
        template_loader.templates['box/rss_description.html'] = 'XXX'
        feeder = RSSTopCategoryListings()
        feeder.box_context = Context({})
        tools.assert_equals('XXX', feeder.item_description(self.listings[0]))

    def test_guid_is_set_properly(self):
        feeder = RSSTopCategoryListings()
        tools.assert_equals(str(self.publishables[-1].pk), feeder.item_guid(self.listings[0]))

