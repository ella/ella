# -*- coding: utf-8 -*-
import os
from time import strftime
from tempfile import mkstemp

from django.conf import settings
from django.core.files.base import ContentFile
from django.utils.translation import ugettext
from djangosanetesting import DatabaseTestCase
from django.contrib.sites.models import Site
from PIL import Image

from ella.photos.models import Photo, Format, FormatedPhoto

from unit_project.test_photos.fixtures import create_photo_formats

class TestPhoto(DatabaseTestCase):

    def setUp(self):
        super(TestPhoto, self).setUp()

        # fixtures
        create_photo_formats(self)

        # "fixtures" aka example photo

        # prepare image in temporary directory
        self.image_file_name = mkstemp(suffix=".jpg", prefix="ella-photo-tests-")[1]
        self.image = Image.new('RGB', (200, 100), "black")
        self.image.save(self.image_file_name, format="jpeg")

        f = open(self.image_file_name)
        file = ContentFile(f.read())
        f.close()

        self.photo = Photo(
            title = u"Example 中文 photo",
            slug = u"example-photo",
            height = 200,
            width = 100,
        )

        self.photo.image.save("bazaaah", file)
        self.photo.save()

        self.thumbnail_path = self.photo.get_thumbnail_path()

    def test_formatted_photo_has_zero_crop_box_if_smaller_than_format(self):
        format = Format.objects.create(
            name='sample',
            max_width=300,
            max_height=300,
            flexible_height=False,
            stretch=False,
            nocrop=False
        )
        format.sites.add(Site.objects.get_current())

        fp = FormatedPhoto(photo=self.photo, format=format)
        fp.generate(False)
        self.assert_equals((0,0,0,0), (fp.crop_left, fp.crop_top, fp.crop_width, fp.crop_height))



    def test_thumbnail_html_retrieval_success(self):
        #TODO: This should be in adimn, not models
        expected_html = u'<a href="%(full)s" class="js-nohashadr thickbox" title="%(title)s" target="_blank"><img src="%(thumb)s" alt="%(name)s" /></a>' % {
            'full' : "%(media)sphotos/%(date)s/%(name)s.jpg" % {
                "name" : u'%s-example-photo' % self.photo.pk,
                "media" : settings.MEDIA_URL,
                "date" : strftime("%Y/%m/%d"),
            },
            'thumb' : "%(media)sphotos/%(date)s/thumb-%(name)s.jpg" % {
                "name" : u'%s-example-photo' % self.photo.pk,
                "media" : settings.MEDIA_URL,
                "date" : strftime("%Y/%m/%d"),
            },
            "title" : u"Example 中文 photo",
            'name' : u"Thumbnail Example 中文 photo",
        }
        self.assert_equals(expected_html, self.photo.thumb())

    def test_retrieving_thumbnail_url_creates_image(self):
        url = self.photo.thumb_url()
        self.assert_equals(True, self.photo.image.storage.exists(self.thumbnail_path))

    def test_thumbnail_not_retrieved_prematurely(self):
        # aka thumbnail not created because thumb_url was not called
        self.assert_equals(False, self.photo.image.storage.exists(self.thumbnail_path))

    def test_thumbnail_path_creation(self):
        self.assert_equals("photos/2008/12/31/thumb-foo.jpg", self.photo.get_thumbnail_path("photos/2008/12/31/foo.jpg"))

    def test_thumbnail_deleted(self):
        url = self.photo.thumb_url()
        self.photo.delete()

        self.assert_equals(False, self.photo.image.storage.exists(self.thumbnail_path))

    def test_thumbnail_html_for_invalid_image(self):
        # be sneaky and delete image
        self.photo.image.storage.delete(self.photo.image.path)

        # now we are not able to detect it's format, BWAHAHA
        expected_html = """<strong>%s</strong>""" % ugettext('Thumbnail not available')
        self.assert_equals(expected_html, self.photo.thumb())

    def test_thumbnail_thumburl_for_nonexisting_image(self):
        self.photo.image.storage.delete(self.photo.image.path)
        self.assert_equals(None, self.photo.thumb_url())

    def test_retrieving_formatted_photos_on_fly(self):
        formatted = self.photo.get_formated_photo("basic")
        self.assert_equals(self.photo, formatted.photo)

    def test_formattedphoto_cleared_when_image_changed(self):
        formatted = self.photo.get_formated_photo("basic")
        self.assert_equals(1, len(self.photo.formatedphoto_set.all()))

        # let us create image again
        f = open(self.image_file_name)
        file = ContentFile(f.read())
        f.close()

        self.photo.image.save("newzaaah", file)
        self.photo.save()

        self.assert_equals(0, len(self.photo.formatedphoto_set.all()))

    def test_formattedphoto_is_none_when_image_destroyed(self):
        # be sneaky and delete image
        self.photo.image.storage.delete(self.photo.image.path)
        self.assert_equals(None, self.photo.get_formated_photo("basic"))

    def test_retrieving_ratio(self):
        self.assert_equals(2, self.photo.ratio())

    def tearDown(self):
        os.remove(self.image_file_name)
        if self.photo.pk:
            self.photo.delete()
        super(TestPhoto, self).tearDown()
