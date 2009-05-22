# -*- coding: utf-8 -*-
from djangosanetesting import DatabaseTestCase

from ella.core.models import Publishable
from ella.core.box import Box
from ella.articles.models import Article

from unit_project.test_core import create_basic_categories, create_and_place_a_publishable


class ArticleBox(Box):
    pass

class TestPublishableBox(DatabaseTestCase):
    def setUp(self):
        super(TestPublishableBox, self).setUp()
        create_basic_categories(self)
        create_and_place_a_publishable(self)

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

        self.assert_equals(template_list, box_publishable._get_template_list())
        self.assert_equals(template_list, box_article._get_template_list())

    def test_box_class_is_specific_to_subclass(self):
        publishable = Publishable.objects.get(pk=self.publishable.pk)
        Article.box_class = ArticleBox
        box = publishable.box_class(publishable, 'box_type', [])
        self.assert_equals(ArticleBox, box.__class__)

