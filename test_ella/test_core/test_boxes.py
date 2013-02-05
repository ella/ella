# -*- coding: utf-8 -*-
from test_ella.cases import RedisTestCase as TestCase
from django.template import Context

from nose import tools

from ella.core.models import Publishable
from ella.core.box import Box
from ella.core.cache.utils import _get_key, KEY_PREFIX
from ella.articles.models import Article

from test_ella.test_core import create_basic_categories, create_and_place_a_publishable
from test_ella import template_loader


class ArticleBox(Box):
    pass

class TestPublishableBox(TestCase):
    def setUp(self):
        super(TestPublishableBox, self).setUp()
        create_basic_categories(self)
        create_and_place_a_publishable(self)

    def tearDown(self):
        super(TestPublishableBox, self).tearDown()
        template_loader.templates = {}

    def test_box_works_for_any_class(self):
        class TestClass(object):
            title = 'Heyoo'
        test_obj = TestClass()
        test_box = Box(test_obj, 'box_type', [])

        tools.assert_equals([
            'box/content_type/testclass/box_type.html',
            'box/content_type/testclass/box.html',
            'box/box_type.html',
            'box/box.html'
        ], test_box._get_template_list())

        template_loader.templates['box/content_type/testclass/box_type.html'] = '{{ object.title}}'
        tools.assert_equals('Heyoo', test_box.render(Context({})))

    def test_box_cache_key_is_prefixed_by_objects_key(self):
        box = Box(self.publishable, 'box_type', [])
        # initialize the box's .params attribute
        box.prepare({})
        tools.assert_true(box.get_cache_key().startswith(_get_key(KEY_PREFIX, self.publishable.content_type, pk=self.publishable.pk)))

    def test_box_template_path_contains_correct_content_type(self):
        publishable = Publishable.objects.get(pk=self.publishable.pk)
        article = publishable.target

        box_publishable = publishable.box_class(publishable, 'box_type', [])
        box_article = Box(article, 'box_type', [])

        template_list = [
            'box/category/nested-category/content_type/articles.article/first-article/box_type.html',
            'box/category/nested-category/content_type/articles.article/box_type.html',
            'box/category/nested-category/content_type/articles.article/box.html',
            'box/content_type/articles.article/first-article/box_type.html',
            'box/content_type/articles.article/box_type.html',
            'box/content_type/articles.article/box.html',
            'box/box_type.html',
            'box/box.html',
        ]

        tools.assert_equals(template_list, box_publishable._get_template_list())
        tools.assert_equals(template_list, box_article._get_template_list())

    def test_box_class_is_specific_to_subclass(self):
        publishable = Publishable.objects.get(pk=self.publishable.pk)
        Article.box_class = ArticleBox
        box = publishable.box_class(publishable, 'box_type', [])
        tools.assert_equals(ArticleBox, box.__class__)

