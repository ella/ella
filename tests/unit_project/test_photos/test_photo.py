# -*- coding: utf-8 -*-
import os
from time import strftime
from tempfile import mkstemp

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

    def test_thumbnail_retrieval(self):
        from django.db import settings
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

    def tearDown(self):
        self.photo.delete()
        super(TestPhoto, self).tearDown()
