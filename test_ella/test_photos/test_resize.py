# -*- coding: utf-8 -*-
from unittest import TestCase
from os import path

from nose import tools

from PIL import Image

from ella.photos.models import Format
from ella.photos.formatter import Formatter

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

class TestPhotoResize(TestCase):

    def setUp(self):
        super(TestPhotoResize, self).setUp()
        self.format = Format(max_height=100, max_width=100)

    def test_custom_bg_color_is_used_for_neg_coords(self):
        i = Image.new('RGB', (200, 200), RED)
        f = Formatter(i, self.format, crop_box=(-50, -50, 50, 50))

        i, crop_box = f.format()
        tools.assert_equals((-50, -50, 50, 50), crop_box)
        tools.assert_equals((100, 100), i.size)
        tools.assert_equals(BLUE, i.getpixel((0, 0)))
        tools.assert_equals(RED, i.getpixel((51, 51)))
        tools.assert_equals(RED, i.getpixel((50, 50)))
        tools.assert_equals(RED, i.getpixel((99, 99)))

    def test_taller_image_gets_cropped_to_ratio(self):
        i = Image.new('RGB', (100, 200), BLACK)
        f = Formatter(i, self.format)

        i, crop_box = f.format()
        tools.assert_equals((0, 50, 100, 150), crop_box)
        tools.assert_equals((100, 100), i.size)

    def test_wider_image_gets_cropped_to_ratio(self):
        i = Image.new('RGB', (200, 100), BLACK)
        f = Formatter(i, self.format)

        i, crop_box = f.format()
        tools.assert_equals((50, 0, 150, 100), crop_box)
        tools.assert_equals((100, 100), i.size)

    def test_bigger_image_gets_shrinked_without_cropping(self):
        i = Image.new('RGB', (200, 200), BLACK)
        f = Formatter(i, self.format)

        i, crop_box = f.format()
        tools.assert_equals(None, crop_box)
        tools.assert_equals((100, 100), i.size)

    def test_smaller_image_remains_untouched(self):
        i = Image.new('RGB', (100, 20), BLACK)
        f = Formatter(i, self.format)

        i, crop_box = f.format()
        tools.assert_equals(None, crop_box)
        tools.assert_equals((100, 20), i.size)

    def test_taller_image_gets_shrinked_to_ratio_with_nocrop(self):
        i = Image.new('RGB', (100, 200), BLACK)
        self.format.nocrop = True
        f = Formatter(i, self.format)

        i, crop_box = f.format()
        tools.assert_equals(None, crop_box)
        tools.assert_equals((50, 100), i.size)

    def test_wider_image_gets_shrinked_to_ratio_with_nocrop(self):
        i = Image.new('RGB', (200, 100), BLACK)
        self.format.nocrop = True
        f = Formatter(i, self.format)

        i, crop_box = f.format()
        tools.assert_equals(None, crop_box)
        tools.assert_equals((100, 50), i.size)

    def test_smaller_image_stretches_with_ratio_intact_with_stretch(self):
        i = Image.new('RGB', (20, 10), BLACK)
        self.format.stretch = True
        f = Formatter(i, self.format)

        i, crop_box = f.format()
        tools.assert_equals(None, crop_box)
        tools.assert_equals((100, 50), i.size)

    def test_flexible_height_doesnt_affect_wider_images(self):
        i = Image.new('RGB', (200, 100), BLACK)
        self.format.flexible_max_height = 200
        self.format.flexible_height = True
        f = Formatter(i, self.format)

        i, crop_box = f.format()
        tools.assert_equals((50, 0, 150, 100), crop_box)
        tools.assert_equals((100, 100), i.size)

    def test_flexible_height_doesnt_raise_exception_no_max_height(self):
        i = Image.new('RGB', (200, 100), BLACK)
        self.format.flexible_max_height = None
        self.format.flexible_height = True
        f = Formatter(i, self.format)

        i, crop_box = f.format()
        tools.assert_equals((100, 100), i.size)

    def test_flexible_height_saves_taller_images(self):
        i = Image.new('RGB', (100, 200), BLACK)
        self.format.flexible_max_height = 200
        self.format.flexible_height = True
        f = Formatter(i, self.format)

        i, crop_box = f.format()
        tools.assert_equals(None, crop_box)
        tools.assert_equals((100, 200), i.size)

    def test_custom_crop_box_is_used(self):
        i = Image.new('RGB', (200, 200), RED)
        f = Formatter(i, self.format, crop_box=(0,0,100,100))
        i.putpixel((99, 99), BLACK)

        i, crop_box = f.format()
        tools.assert_equals((0,0,100,100), crop_box)
        tools.assert_equals((100, 100), i.size)
        tools.assert_equals(BLACK, i.getpixel((99,99)))

    def test_important_box_is_used(self):
        i = Image.new('RGB', (200, 100), RED)
        f = Formatter(i, self.format, important_box=(0,0,100,100))
        i.putpixel((99, 99), BLACK)

        i, crop_box = f.format()
        tools.assert_equals((0,0,100,100), crop_box)
        tools.assert_equals((100, 100), i.size)
        tools.assert_equals(BLACK, i.getpixel((99,99)))

    def test_important_box_is_used_for_other_positive_x_motion_as_well(self):
        i = Image.new('RGB', (200, 100), RED)
        f = Formatter(i, self.format, important_box=(100,0,200,100))
        i.putpixel((100, 0), BLACK)

        i, crop_box = f.format()
        tools.assert_equals((100,0,200,100), crop_box)
        tools.assert_equals((100, 100), i.size)
        tools.assert_equals(BLACK, i.getpixel((0,0)))

    def test_important_box_is_used_for_positive_y_motion_as_well(self):
        i = Image.new('RGB', (100, 200), RED)
        f = Formatter(i, self.format, important_box=(0,100,100,200))
        i.putpixel((0, 100), BLACK)

        i, crop_box = f.format()
        tools.assert_equals((0,100,100,200), crop_box)
        tools.assert_equals((100, 100), i.size)
        tools.assert_equals(BLACK, i.getpixel((0,0)))

class TestPhotoResizeWithRotate(TestCase):

    def setUp(self):
        super(TestPhotoResizeWithRotate, self).setUp()
        self.base = path.dirname(path.abspath(__file__))
        self.format = Format(max_height=100, max_width=100)

    def get_image_and_formatter(self, name):
        o = Image.open(path.join(self.base, 'data', name))
        f = Formatter(o, self.format)
        return o, f

    def test_as_data_we_have_white_box_on_the_left_black_box_on_the_right(self):
        i, f = self.get_image_and_formatter('rotate1.jpeg')

        tools.assert_equals((20, 10), i.size)
        tools.assert_equals(WHITE, i.getpixel((5, 5)))
        tools.assert_equals(BLACK, i.getpixel((15, 5)))

    def test_plain_jpeg_is_not_rotated(self):
        o, f = self.get_image_and_formatter('rotate1.jpeg')
        i, c = f.format()

        tools.assert_equals((20, 10), i.size)
        tools.assert_equals(WHITE, i.getpixel((5, 5)))
        tools.assert_equals(BLACK, i.getpixel((15, 5)))

    def test_jpeg_with_exit_rotation_info_3_is_rotated_180_degrees(self):
        o, f = self.get_image_and_formatter('rotate3.jpeg')
        i, c = f.format()

        tools.assert_equals((20, 10), i.size)
        tools.assert_equals(BLACK, i.getpixel((5, 5)))
        tools.assert_equals(WHITE, i.getpixel((15, 5)))

    def test_jpeg_with_exit_rotation_info_6_is_rotated_90_degrees_clockwise(self):
        o, f = self.get_image_and_formatter('rotate6.jpeg')
        i, c = f.format()

        tools.assert_equals((10, 20), i.size)
        tools.assert_equals(WHITE, i.getpixel((5, 5)))
        tools.assert_equals(BLACK, i.getpixel((5, 15)))

    def test_jpeg_with_exit_rotation_info_8_is_rotated_90_degrees_counter_clockwise(self):
        o, f = self.get_image_and_formatter('rotate8.jpeg')
        i, c = f.format()

        tools.assert_equals((10, 20), i.size)
        tools.assert_equals(BLACK, i.getpixel((5, 5)))
        tools.assert_equals(WHITE, i.getpixel((5, 15)))

