# -*- coding: utf-8 -*-
from djangosanetesting import DatabaseTestCase

from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import slugify
from django.template import TemplateDoesNotExist

from unit_project.test_core import create_basic_categories, create_and_place_a_publishable
from unit_project import template_loader

class ViewsTestCase(DatabaseTestCase):
    def setUp(self):
        super(ViewsTestCase, self).setUp()
        create_basic_categories(self)
        create_and_place_a_publishable(self)

    def tearDown(self):
        super(ViewsTestCase, self).tearDown()
        template_loader.templates = {}

class TestCategoryDetail(ViewsTestCase):
    def test_fail_on_no_template(self):
        self.assert_raises(TemplateDoesNotExist, self.client.get, '/')

    def test_template_overloading(self):
        template_loader.templates['page/category.html'] = 'page/category.html'
        template_loader.templates['page/category/ni-hao-category/category.html'] = 'page/category/ni-hao-category/category.html'
        response = self.client.get('/')
        self.assert_equals('page/category/ni-hao-category/category.html', response.content)

    def test_second_nested_template_overloading(self):
        tp = 'nested-category/second-nested-category'
        template_loader.templates['page/category.html'] = 'page/category.html'
        template_loader.templates['page/category/%s/category.html'%tp] = 'page/category/%s/category.html'%tp
        response = self.client.get('/%s/'%tp)
        self.assert_equals('page/category/%s/category.html'%tp, response.content)

    def test_homepage_context(self):
        template_loader.templates['page/category.html'] = ''
        response = self.client.get('/')
        self.assert_true('category' in response.context)
        self.assert_equals(self.category, response.context['category'])

    def test_second_nested_category_view(self):
        template_loader.templates['page/category.html'] = ''
        response = self.client.get('/nested-category/second-nested-category/')
        self.assert_true('category' in response.context)
        self.assert_equals(self.category_nested_second, response.context['category'])

class TestObjectDetailTemplateOverride(ViewsTestCase):
    def setUp(self):
        super(TestObjectDetailTemplateOverride, self).setUp()
        publ = self.publishable
        ct = publ._meta.app_label + '.' + publ._meta.module_name

        self.templates = (
            'page/object.html',
            'page/content_type/%s/object.html' % ct,
            'page/category/%s/object.html' % publ.category.path,
            'page/category/%s/content_type/%s/object.html' % (publ.category.path, ct),
            'page/category/%s/content_type/%s/%s/object.html' % (publ.category.path, ct, publ.slug)
        )
        for i, t in enumerate(self.templates):
            template_loader.templates[t] = i

        self.url = publ.get_absolute_url()

    def test_fallback(self):
        for t in self.templates[-4:]:
            del template_loader.templates[t]
        self.assert_equals('0', self.client.get(self.url).content)

    def test_ct(self):
        for t in self.templates[-3:]:
            del template_loader.templates[t]
        self.assert_equals('1', self.client.get(self.url).content)

    def test_category(self):
        for t in self.templates[-2:]:
            del template_loader.templates[t]
        self.assert_equals('2', self.client.get(self.url).content)

    def test_category_ct(self):
        del template_loader.templates[self.templates[-1]]
        self.assert_equals('3', self.client.get(self.url).content)

    def test_category_ct_slug(self):
        self.assert_equals('4', self.client.get(self.url).content)

class TestObjectDetail(ViewsTestCase):
    def setUp(self):
        super(TestObjectDetail, self).setUp()
        template_loader.templates['page/object.html'] = ''

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

