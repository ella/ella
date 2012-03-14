from django.template import Node
from django.test import TestCase
from django.conf import settings

from nose import tools, SkipTest

from ella.photos.templatetags.photos import _parse_img, ImgTag

from test_ella.test_photos.fixtures import create_photo_formats

class TestImgParsing(TestCase):
    def setUp(self):
        super(TestImgParsing, self).setUp()
        create_photo_formats(self)

    def test_node_gets_passed_correct_params(self):
        img_node = _parse_img('img basic for VAR as VAR_NAME'.split())
        tools.assert_is_instance(img_node, ImgTag)
        tools.assert_equals(self.basic_format, img_node.format)

    def test_return_empty_node_on_unknown_format(self):
        if settings.TEMPLATE_DEBUG:
            raise SkipTest()
        img_node = _parse_img('img unknownformat for VAR as VAR_NAME'.split())
        tools.assert_equals(Node, img_node.__class__)
