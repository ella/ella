# -*- coding: utf-8 -*-
import os
from tempfile import mkstemp

from djangosanetesting import DatabaseTestCase
from PIL import Image

from ella.photos.models import Photo

class TestPhoto(DatabaseTestCase):

    def setUp(self):
        super(TestPhoto, self).setUp()

        self.prepare_image()

        self.photo = Photo(
            title = u"Example 中文 photo",
            slug = u"example-photo",
            image = self.image_file_name,
            height = 200,
            width = 100,
        )

    def prepare_image(self):
        """
        Prepare example image for tests as we're not able to operate only in-memory
        (ImageField requires filename)
        """
        from django.db import settings
        self.image_file_name = mkstemp(suffix=".jpg", prefix="ella-photo-tests-", dir=settings.MEDIA_ROOT)[1]
        self.image = Image.new('RGB', (200, 100), "black")
        self.image.save(self.image_file_name, format="jpeg")
        self.image.seek(0)

    def test_saving_clears_image(self):
        self.photo.save()
        self.assert_equals(False, os.path.exists(self.image_file_name))

    

#    def tearDown(self):
#        super(TestPhoto, self).tearDown()
