# -*- coding: utf-8 -*-
import os
from time import strftime
from tempfile import mkstemp

from django.conf import settings
from django.core.files.base import ContentFile
from djangosanetesting import DatabaseTestCase
from PIL import Image

from ella.photos.models import Photo

class TestPhoto(DatabaseTestCase):

    def setUp(self):
        super(TestPhoto, self).setUp()

        # prepare image in temporary directory
        self.image_file_name = mkstemp(suffix=".jpg", prefix="ella-photo-tests-")[1]
        self.image = Image.new('RGB', (200, 100), "black")
        self.image.save(self.image_file_name, format="jpeg")

        f = open(self.image_file_name)
        file = ContentFile(f.read())
        f.close()
        
        os.remove(self.image_file_name)

        self.photo = Photo(
            title = u"Example 中文 photo",
            slug = u"example-photo",
            height = 200,
            width = 100,
        )

        self.photo.image.save("bazaaah", file)
        self.photo.save()

    def test_thumbnail_html_retrieval(self):
        expected_html = u'<a href="%(full)s"><img src="%(thumb)s" alt="%(name)s" /></a>' % {
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
            'name' : u"Thumbnail Example 中文 photo",
        }
        self.assert_equals(expected_html, self.photo.thumb())

    def test_retrieving_thumbnail_url_creates_image(self):
        url = self.photo.thumb_url()
        self.assert_equals(True, self.photo.image.storage.exists(self.photo.get_thumbnail_path()))

    def test_thumbnail_not_retrieved_prematurely(self):
        # aka thumbnail not created because thumb_url was not called
        self.assert_equals(False, self.photo.image.storage.exists(self.photo.get_thumbnail_path()))

    def test_thumbnail_path_creation(self):
        self.assert_equals("photos/2008/12/31/thumb-foo.jpg", self.photo.get_thumbnail_path("photos/2008/12/31/foo.jpg"))

    

    def tearDown(self):
        self.photo.delete()
        super(TestPhoto, self).tearDown()
