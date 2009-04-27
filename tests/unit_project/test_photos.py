# -*- coding: utf-8 -*-
from djangosanetesting import UnitTestCase

from PIL import Image

from ella.photos.models import Format
from ella.photos.formatter import Formatter

class TestPhotoResize(UnitTestCase):

    def setUp(self):
        super(TestPhotoResize, self).setUp()
        self.format = Format(max_height=100, max_width=100)

    def test_taller_image_gets_cropped_to_ratio(self):
        i = Image.new('RGB', (100, 200), "black")
        f = Formatter(i, self.format)

        self.assert_equals((0, 50, 100, 150), f.get_crop_box())
        i = f.format()
        self.assert_equals((100, 100), i.size)

    def test_wider_image_gets_cropped_to_ratio(self):
        i = Image.new('RGB', (200, 100), "black")
        f = Formatter(i, self.format)

        self.assert_equals((50, 0, 150, 100), f.get_crop_box())
        i = f.format()
        self.assert_equals((100, 100), i.size)

    def test_bigger_image_gets_shrinked_without_cropping(self):
        i = Image.new('RGB', (200, 200), "black")
        f = Formatter(i, self.format)

        self.assert_equals(None, f.get_crop_box())
        i = f.format()
        self.assert_equals((100, 100), i.size)

    def test_smaller_image_remains_untouched(self):
        i = Image.new('RGB', (100, 20), "black")
        f = Formatter(i, self.format)

        self.assert_equals(None, f.get_crop_box())
        i = f.format()
        self.assert_equals((100, 20), i.size)

    def test_taller_image_gets_shrinked_to_ratio_with_nocrop(self):
        i = Image.new('RGB', (100, 200), "black")
        self.format.nocrop = True
        f = Formatter(i, self.format)

        self.assert_equals(None, f.get_crop_box())
        i = f.format()
        self.assert_equals((50, 100), i.size)

    def test_wider_image_gets_shrinked_to_ratio_with_nocrop(self):
        i = Image.new('RGB', (200, 100), "black")
        self.format.nocrop = True
        f = Formatter(i, self.format)

        self.assert_equals(None, f.get_crop_box())
        i = f.format()
        self.assert_equals((100, 50), i.size)

    def test_smaller_image_stretches_with_ratio_intact_with_stretch(self):
        i = Image.new('RGB', (20, 10), "black")
        self.format.stretch = True
        f = Formatter(i, self.format)

        self.assert_equals(None, f.get_crop_box())
        i = f.format()
        self.assert_equals((100, 50), i.size)

