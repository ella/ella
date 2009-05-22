# -*- coding: utf-8 -*-
from djangosanetesting import DatabaseTestCase

from PIL import Image

from ella.photos.models import Photo

class TestPhoto(DatabaseTestCase):

    def setUp(self):
        super(TestPhoto, self).setUp()
        self.image = Image.new('RGB', (200, 100), "black")
        self.photo = Photo(
            title = u"Example 中文 photo",
            slug = u"example-photo",
        )

    def test_saving(self):
        pass
