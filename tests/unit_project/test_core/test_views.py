# -*- coding: utf-8 -*-
from djangosanetesting import DatabaseTestCase

from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import slugify

from unit_project.test_core import create_basic_categories, create_and_place_a_publishable

class TestCoreViews(DatabaseTestCase):
    def setUp(self):
        super(TestCoreViews, self).setUp()
        create_basic_categories(self)
        create_and_place_a_publishable(self)

    def test_homepage(self):
        response = self.client.get('/')
        self.assert_true('category' in response.context)
        self.assert_equals(self.category, response.context['category'])

    def test_object_detail(self):
        response = self.client.get('/nested-category/2008/1/10/articles/first-article/')

        self.assert_true('placement' in response.context)
        self.assert_equals(self.placement, response.context['placement'])

        self.assert_true('category' in response.context)
        self.assert_equals(self.publishable.category, response.context['category'])

        self.assert_true('object' in response.context)
        self.assert_equals(self.publishable, response.context['object'])

        self.assert_true('content_type' in response.context)
        self.assert_equals(
                ContentType.objects.get_for_model(self.publishable),
                response.context['content_type']
        )

        self.assert_true('content_type_name' in response.context)
        self.assert_equals(
                slugify(self.publishable._meta.verbose_name_plural),
                response.context['content_type_name']
        )

    def test_static_object_detail(self):
        self.placement.static = True
        self.placement.save()
        response = self.client.get('/nested-category/static/articles/first-article/')

        self.assert_true('placement' in response.context)
        self.assert_equals(self.placement, response.context['placement'])

        self.assert_true('category' in response.context)
        self.assert_equals(self.publishable.category, response.context['category'])

        self.assert_true('object' in response.context)
        self.assert_equals(self.publishable, response.context['object'])

        self.assert_true('content_type' in response.context)
        self.assert_equals(
                ContentType.objects.get_for_model(self.publishable),
                response.context['content_type']
        )

        self.assert_true('content_type_name' in response.context)
        self.assert_equals(
                slugify(self.publishable._meta.verbose_name_plural),
                response.context['content_type_name']
        )

