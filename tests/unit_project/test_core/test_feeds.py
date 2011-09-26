# -*- coding: utf-8 -*-
from PIL import Image

from djangosanetesting import DatabaseTestCase

from django.core.urlresolvers import reverse
from django.http import HttpRequest

from ella.core.models import Listing
from ella.core.feeds import RSSTopCategoryListings
from ella.photos.models import Photo, Format

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
        
        self._feeder = RSSTopCategoryListings('test', HttpRequest())

    def _set_photo(self):
        from tempfile import mkstemp
        from django.core.files.base import ContentFile
        
        image_file_name = mkstemp(suffix=".jpg", prefix="ella-feeds-tests-")[1]
        image = Image.new('RGB', (200, 100), "black")
        image.save(image_file_name, format="jpeg")

        f = open(image_file_name)
        file = ContentFile(f.read())
        f.close()

        photo = Photo(
            title = u"Example 中文 photo",
            slug = u"example-photo",
            height = 200,
            width = 100,
        )

        photo.image.save("bazaaah", file)
        photo.save()
        
        self.publishable.photo = photo
        self.publishable.save()

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

    def test_get_enclosure_uses_original_when_format_not_set(self):
        self._set_photo()
        self.assert_true(self.publishable.photo is not None)
        original = self.publishable.photo.image
        new = self._feeder.get_enclosure_image(self.only_publishable, enc_format=None)
        self.assert_equals(unicode(original), unicode(new))
    
    def test_get_enclosure_uses_original_when_format_not_found(self):
        non_existent_format_name = 'aaa'
        self._set_photo()
        self.assert_true(self.publishable.photo is not None)
        original = self.publishable.photo.image
        new = self._feeder.get_enclosure_image(self.only_publishable, enc_format=non_existent_format_name)
        self.assert_equals(unicode(original), unicode(new))
    
    def test_get_enclosure_uses_formated_photo_when_format_available(self):
        existent_format_name = 'enc_format'
        f = Format.objects.create(name=existent_format_name, max_width=10, max_height=10,
            flexible_height=False, stretch=False, nocrop=False)
        f.sites = [self.site_id]
        
        self._set_photo()
        self.assert_true(self.publishable.photo is not None)
        original = self.publishable.photo.image
        new = self._feeder.get_enclosure_image(self.only_publishable, enc_format=existent_format_name)
        self.assert_not_equals(unicode(original), unicode(new))
    
    def test_get_enclosure_returns_none_when_no_image_set(self):
        self.assert_equals(self._feeder.get_enclosure_image(self.only_publishable), None)
    
    


