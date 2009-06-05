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

        i, crop_box = f.format()
        self.assert_equals((0, 50, 100, 150), crop_box)
        self.assert_equals((100, 100), i.size)

    def test_wider_image_gets_cropped_to_ratio(self):
        i = Image.new('RGB', (200, 100), "black")
        f = Formatter(i, self.format)

        i, crop_box = f.format()
        self.assert_equals((50, 0, 150, 100), crop_box)
        self.assert_equals((100, 100), i.size)

    def test_bigger_image_gets_shrinked_without_cropping(self):
        i = Image.new('RGB', (200, 200), "black")
        f = Formatter(i, self.format)

        i, crop_box = f.format()
        self.assert_equals(None, crop_box)
        self.assert_equals((100, 100), i.size)

    def test_smaller_image_remains_untouched(self):
        i = Image.new('RGB', (100, 20), "black")
        f = Formatter(i, self.format)

        i, crop_box = f.format()
        self.assert_equals(None, crop_box)
        self.assert_equals((100, 20), i.size)

    def test_taller_image_gets_shrinked_to_ratio_with_nocrop(self):
        i = Image.new('RGB', (100, 200), "black")
        self.format.nocrop = True
        f = Formatter(i, self.format)

        i, crop_box = f.format()
        self.assert_equals(None, crop_box)
        self.assert_equals((50, 100), i.size)

    def test_wider_image_gets_shrinked_to_ratio_with_nocrop(self):
        i = Image.new('RGB', (200, 100), "black")
        self.format.nocrop = True
        f = Formatter(i, self.format)

        i, crop_box = f.format()
        self.assert_equals(None, crop_box)
        self.assert_equals((100, 50), i.size)

    def test_smaller_image_stretches_with_ratio_intact_with_stretch(self):
        i = Image.new('RGB', (20, 10), "black")
        self.format.stretch = True
        f = Formatter(i, self.format)

        i, crop_box = f.format()
        self.assert_equals(None, crop_box)
        self.assert_equals((100, 50), i.size)

    def test_flexible_height_doesnt_affect_wider_images(self):
        i = Image.new('RGB', (200, 100), "black")
        self.format.flexible_max_height = 200
        self.format.flexible_height = True
        f = Formatter(i, self.format)

        i, crop_box = f.format()
        self.assert_equals((50, 0, 150, 100), crop_box)
        self.assert_equals((100, 100), i.size)

    def test_flexible_height_saves_taller_images(self):
        i = Image.new('RGB', (100, 200), "black")
        self.format.flexible_max_height = 200
        self.format.flexible_height = True
        f = Formatter(i, self.format)

        i, crop_box = f.format()
        self.assert_equals(None, crop_box)
        self.assert_equals((100, 200), i.size)

    def test_custom_crop_box_is_used(self):
        i = Image.new('RGB', (200, 200), "red")
        f = Formatter(i, self.format, crop_box=(0,0,100,100))
        i.putpixel((99, 99), 0)

        i, crop_box = f.format()
        self.assert_equals((0,0,100,100), crop_box)
        self.assert_equals((100, 100), i.size)
        self.assert_equals((0,0,0), i.getpixel((99,99)))

    def test_important_box_is_used(self):
        i = Image.new('RGB', (200, 100), "red")
        f = Formatter(i, self.format, important_box=(0,0,100,100))
        i.putpixel((99, 99), 0)

        i, crop_box = f.format()
        self.assert_equals((0,0,100,100), crop_box)
        self.assert_equals((100, 100), i.size)
        self.assert_equals((0,0,0), i.getpixel((99,99)))

    def test_important_box_is_used_for_other_positive_x_motion_as_well(self):
        i = Image.new('RGB', (200, 100), "red")
        f = Formatter(i, self.format, important_box=(100,0,200,100))
        i.putpixel((100, 0), 0)

        i, crop_box = f.format()
        self.assert_equals((100,0,200,100), crop_box)
        self.assert_equals((100, 100), i.size)
        self.assert_equals((0,0,0), i.getpixel((0,0)))

    def test_important_box_is_used_for_positive_y_motion_as_well(self):
        i = Image.new('RGB', (100, 200), "red")
        f = Formatter(i, self.format, important_box=(0,100,100,200))
        i.putpixel((0, 100), 0)

        i, crop_box = f.format()
        self.assert_equals((0,100,100,200), crop_box)
        self.assert_equals((100, 100), i.size)
        self.assert_equals((0,0,0), i.getpixel((0,0)))

