# -*- coding: utf-8 -*-
from PIL import Image

from django.core.files.base import ContentFile
from test_ella.cases import RedisTestCase as TestCase
from django.contrib.sites.models import Site

from nose import tools

from ella.photos.models import Format, FormatedPhoto, redis, REDIS_FORMATTED_PHOTO_KEY
from ella.photos.conf import photos_settings

from test_ella.test_photos.fixtures import create_photo_formats, create_photo


class TestPhoto(TestCase):

    def setUp(self):
        super(TestPhoto, self).setUp()

        # fixtures
        create_photo_formats(self)

        create_photo(self)

    def tearDown(self):
        photos_settings.FORMATED_PHOTO_FILENAME = None
        if self.photo.pk:
            self.photo.delete()
        super(TestPhoto, self).tearDown()
        if redis:
            redis.flushdb()

    def test_formated_photo_from_master_format_is_used(self):
        master_format = Format.objects.create(
            name='sample',
            max_width=300,
            max_height=200,
            flexible_height=False,
            stretch=False,
            nocrop=False
        )
        slave_format = Format.objects.create(
            name='slave',
            max_width=300,
            max_height=100,
            flexible_height=False,
            stretch=False,
            nocrop=False,
            master=master_format
        )
        master_fp = FormatedPhoto(photo=self.photo, format=master_format)
        p2 = create_photo(self, color=(123, 123, 123), size=(300, 200))
        p2.image.open()
        master_fp.image.save(p2.image.name, p2.image)
        master_fp.save()

        fp = FormatedPhoto(photo=self.photo, format=slave_format)
        fp.save()

        fp.image.open()
        i = Image.open(fp.image)
        tools.assert_equals((123, 123, 123), i.getpixel((10, 10)))
        tools.assert_equals((300, 100), i.size)
        p2.image.close()

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
        tools.assert_equals((0, 0, 0, 0), (fp.crop_left, fp.crop_top, fp.crop_width, fp.crop_height))

    def test_formated_filename_can_be_overridden(self):
        photos_settings.FORMATED_PHOTO_FILENAME = lambda fp: 'XXX.jpg'
        formatted = FormatedPhoto.objects.get_photo_in_format(self.photo, self.basic_format)
        tools.assert_true('url' in formatted)
        tools.assert_true(formatted['url'].endswith('XXX.jpg'))

    def test_retrieving_formatted_photos_on_fly(self):
        formatted = FormatedPhoto.objects.get_photo_in_format(self.photo, self.basic_format)
        tools.assert_true('url' in formatted)
        if redis:
            expected = {
                'height': '20',
                'width': '20',
                'url': '/static/photos/2012/02/14/1-1-example-photo_12.jpg',
            }
            actual = redis.hgetall(REDIS_FORMATTED_PHOTO_KEY % (self.photo.id, self.basic_format.id))
            tools.assert_equals(expected.keys(), actual.keys())
            tools.assert_equals(expected['width'], actual['width'])
            tools.assert_equals(expected['height'], actual['height'])

    def test_formattedphoto_cleared_when_image_changed(self):
        FormatedPhoto.objects.get_photo_in_format(self.photo, self.basic_format)
        tools.assert_equals(1, len(self.photo.formatedphoto_set.all()))

        # let us create image again
        self.photo.image.open()
        file = ContentFile(self.photo.image.read())

        self.photo.image.save("newzaaah", file)
        self.photo.save()

        tools.assert_equals(0, len(self.photo.formatedphoto_set.all()))

    def test_formattedphoto_cleared_when_format_changed(self):
        FormatedPhoto.objects.get_photo_in_format(self.photo, self.basic_format)
        tools.assert_equals(1, len(self.basic_format.formatedphoto_set.all()))
        self.basic_format.nocrop = True
        self.basic_format.save()
        tools.assert_equals(0, len(self.basic_format.formatedphoto_set.all()))

    def test_retrieving_ratio(self):
        tools.assert_equals(2, self.photo.ratio())
