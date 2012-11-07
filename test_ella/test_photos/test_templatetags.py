from django.template import Node, Context
from test_ella.cases import RedisTestCase as TestCase
from django.conf import settings

from nose import tools, SkipTest

from ella.photos.templatetags.photos import _parse_img, ImgTag, _parse_image, ImageTag
from ella.photos.models import redis, REDIS_PHOTO_KEY, REDIS_FORMATTED_PHOTO_KEY

from test_ella.test_photos.fixtures import create_photo_formats

class TestImageParsing(TestCase):
    def setUp(self):
        super(TestImageParsing, self).setUp()
        create_photo_formats(self)

    def tearDown(self):
        super(TestImageParsing, self).tearDown()
        if redis:
            redis.flushdb()

    def test_format_is_resolved_if_literal_string(self):
        image_node = _parse_image('image some_photo in "basic" as var_name'.split())
        tools.assert_true(isinstance(image_node, ImageTag))
        tools.assert_equals(self.basic_format, image_node.format)

    def test_photo_id_and_format_picked_up_from_context(self):
        if not redis:
            raise SkipTest()
        redis.hmset(REDIS_FORMATTED_PHOTO_KEY % (42, self.basic_format.pk), {'sentinel': 42})
        redis.hmset(REDIS_PHOTO_KEY % 42, {'orig_sentinel': 42})

        c = Context({'article': {'photo_id': 42, 'photo': 'not-42'}, 'image_format': self.basic_format})
        image_node = _parse_image('image article.photo in image_format as var_name'.split())

        tools.assert_true(isinstance(image_node, ImageTag))
        tools.assert_equals('', image_node.render(c))
        tools.assert_true('var_name' in c)
        tools.assert_equals({'sentinel': '42', 'original': {'orig_sentinel': '42'}}, c['var_name'])


    def test_photo_and_format_name_picked_up_from_context(self):
        if not redis:
            raise SkipTest()
        redis.hmset(REDIS_FORMATTED_PHOTO_KEY % (42, self.basic_format.pk), {'sentinel': 42})
        redis.hmset(REDIS_PHOTO_KEY % 42, {'orig_sentinel': 42})

        c = Context({'article': {'photo': 42}, 'image_format': 'basic'})
        image_node = _parse_image('image article.photo in image_format as var_name'.split())

        tools.assert_true(isinstance(image_node, ImageTag))
        tools.assert_equals('', image_node.render(c))
        tools.assert_true('var_name' in c)
        tools.assert_equals({'sentinel': '42', 'original': {'orig_sentinel': '42'}}, c['var_name'])


class TestImgParsing(TestCase):
    def setUp(self):
        super(TestImgParsing, self).setUp()
        create_photo_formats(self)

    def test_node_gets_passed_correct_params(self):
        img_node = _parse_img('img basic for VAR as VAR_NAME'.split())
        tools.assert_true(isinstance(img_node, ImgTag))
        tools.assert_equals(self.basic_format, img_node.format)

    def test_return_empty_node_on_unknown_format(self):
        if settings.TEMPLATE_DEBUG:
            raise SkipTest()
        img_node = _parse_img('img unknownformat for VAR as VAR_NAME'.split())
        tools.assert_equals(Node, img_node.__class__)
