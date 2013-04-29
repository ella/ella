# -*- coding: utf-8 -*-

from datetime import datetime
from test_ella.cases import RedisTestCase as TestCase

from nose import tools, SkipTest

from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import slugify
from django.template import TemplateDoesNotExist

from ella.core.models import Listing
from ella.utils import timezone

from test_ella.test_core import create_basic_categories, create_and_place_a_publishable, \
        create_and_place_more_publishables, list_all_publishables_in_category_by_hour
from test_ella import template_loader

from ella.core.models import Category, Author
from ella.core.views import get_templates
from ella.core.signals import object_rendering, object_rendered
from ella.core.cache import utils

class ViewsTestCase(TestCase):
    def setUp(self):
        super(ViewsTestCase, self).setUp()
        create_basic_categories(self)
        create_and_place_a_publishable(self)
        self.signals_received = {}
        object_rendering.connect(self.object_rendering)
        object_rendered.connect(self.object_rendered)

    def object_rendered(self, *args, **kwargs):
        self.signals_received.setdefault('object_rendered', []).append((args, kwargs))

    def object_rendering(self, *args, **kwargs):
        self.signals_received.setdefault('object_rendering', []).append((args, kwargs))

    def tearDown(self):
        super(ViewsTestCase, self).tearDown()
        template_loader.templates = {}
        object_rendering.disconnect(self.object_rendering)
        object_rendered.disconnect(self.object_rendered)
        utils.PUBLISHABLE_CT = None

class TestAuthorView(ViewsTestCase):
    def test_author_view(self):
        author = Author.objects.create(slug='some-author')
        create_and_place_more_publishables(self)
        for p in self.publishables:
            p.authors.add(author)
        list_all_publishables_in_category_by_hour(self)

        template_loader.templates['page/author.html'] = 'page/category.html'
        response = self.client.get(author.get_absolute_url())
        tools.assert_true('listings' in response.context)
        tools.assert_equals(set(p.pk for p in self.publishables), set(l.publishable.pk for l in response.context['listings']))

class TestCategoryDetail(ViewsTestCase):
    def test_fail_on_no_template(self):
        tools.assert_raises(TemplateDoesNotExist, self.client.get, '/')

    def test_template_overloading(self):
        template_loader.templates['page/category.html'] = 'page/category.html'
        template_loader.templates['page/category/ni-hao-category/%s' % self.category.template] = 'page/category/ni-hao-category/category.html'
        response = self.client.get('/')
        tools.assert_equals('page/category/ni-hao-category/category.html', response.content)

    def test_signals_fired_for_homepage(self):
        template_loader.templates['page/category.html'] = 'page/category.html'
        self.client.get('/')
        tools.assert_equals(1, len(self.signals_received['object_rendering']))
        tools.assert_equals(1, len(self.signals_received['object_rendered']))

        kwargs = self.signals_received['object_rendered'][0][1]
        tools.assert_equals(set(['sender', 'request', 'category', 'publishable', 'signal']), set(kwargs.keys()))
        tools.assert_equals(self.category, kwargs['category'])
        tools.assert_equals(Category, kwargs['sender'])
        tools.assert_equals(None, kwargs['publishable'])

    def test_second_nested_template_overloading(self):
        tp = 'nested-category/second-nested-category'
        ctp = self.category_nested_second.template
        template_loader.templates['page/category.html'] = 'page/category.html'
        template_loader.templates['page/category/%s/%s' % (tp, ctp)] = 'page/category/%s/category.html' % tp
        response = self.client.get('/%s/' % tp)
        tools.assert_equals('page/category/%s/category.html' % tp, response.content)

    def test_homepage_context(self):
        template_loader.templates['page/category.html'] = ''
        response = self.client.get('/')
        tools.assert_true('category' in response.context)
        tools.assert_equals(self.category, response.context['category'])

    def test_second_nested_category_view(self):
        template_loader.templates['page/category.html'] = ''
        response = self.client.get('/nested-category/second-nested-category/')
        tools.assert_true('category' in response.context)
        tools.assert_equals(self.category_nested_second, response.context['category'])

    def test_category_template_is_used_in_view(self):
        self.category.template = 'static_page.html'
        self.category.save()
        template_loader.templates['page/category.html'] = 'category.html'
        template_loader.templates['page/static_page.html'] = 'static_page.html'
        response = self.client.get('/')
        tools.assert_equals('static_page.html', response.content)


class TestEmptyHomepage(TestCase):
    def test_404_is_shown_on_debug_off(self):
        from django.conf import settings
        orig_debug = settings.DEBUG
        settings.DEBUG = False
        template_loader.templates['404.html'] = '404.html'
        response = self.client.get('/')
        tools.assert_equals('404.html', response.content)
        settings.DEBUG = orig_debug

    def test_welcome_page_is_shown_as_hompage_on_debug(self):
        from django.conf import settings
        orig_debug = settings.DEBUG
        settings.DEBUG = True
        template_loader.templates['debug/empty_homepage.html'] = 'empty_homepage.html'
        response = self.client.get('/')
        tools.assert_equals('empty_homepage.html', response.content)
        settings.DEBUG = orig_debug


class TestListContentType(ViewsTestCase):
    def setUp(self):
        super(TestListContentType, self).setUp()
        create_and_place_more_publishables(self)
        list_all_publishables_in_category_by_hour(self, category=self.category)

    def test_without_home_listings_first_page_is_an_archive(self):
        self.category_nested_second.app_data.setdefault('ella', {})['no_home_listings'] = True
        self.category_nested_second.save()
        template_loader.templates['page/listing.html'] = ''
        Listing.objects.all().update(category=self.category_nested_second)
        response = self.client.get('/nested-category/second-nested-category/?p=1')
        tools.assert_true('listings' in response.context)
        tools.assert_equals(self.listings, response.context['listings'])

    def test_only_nested_category_and_year_returns_all_listings(self):
        template_loader.templates['page/listing.html'] = ''
        Listing.objects.all().update(category=self.category_nested_second)
        response = self.client.get('/nested-category/second-nested-category/2008/')
        tools.assert_true('listings' in response.context)
        tools.assert_equals(self.listings, response.context['listings'])

    def test_incorrect_page_number_raises_404(self):
        template_loader.templates['404.html'] = ''
        response = self.client.get('/2008/', {'p': 200})
        tools.assert_equals(404, response.status_code)


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
        tools.assert_equals('0', self.client.get(self.url).content)

    def test_ct(self):
        for t in self.templates[-3:]:
            del template_loader.templates[t]
        tools.assert_equals('1', self.client.get(self.url).content)

    def test_category(self):
        for t in self.templates[-2:]:
            del template_loader.templates[t]
        tools.assert_equals('2', self.client.get(self.url).content)

    def test_category_ct(self):
        del template_loader.templates[self.templates[-1]]
        tools.assert_equals('3', self.client.get(self.url).content)

    def test_category_ct_slug(self):
        tools.assert_equals('4', self.client.get(self.url).content)

class TestObjectDetail(ViewsTestCase):
    def setUp(self):
        super(TestObjectDetail, self).setUp()
        template_loader.templates['page/object.html'] = ''

    def test_timezone_localized_url(self):
        if not timezone.use_tz:
            raise SkipTest()
        from test_ella import template_loader
        template_loader.templates['page/object.html'] = 'object.html'
        self.publishable.publish_from = timezone.localize(datetime(2013, 4, 25, 0, 0, 0))
        self.publishable.save()

        tools.assert_equals('/nested-category/2013/4/25/first-article/', self.publishable.get_absolute_url())
        tools.assert_equals(200, self.client.get('/nested-category/2013/4/25/first-article/').status_code)

    def test_signals_fired_for_detail(self):
        self.client.get('/nested-category/2008/1/10/first-article/')
        tools.assert_equals(1, len(self.signals_received['object_rendering']))
        tools.assert_equals(1, len(self.signals_received['object_rendered']))

        kwargs = self.signals_received['object_rendered'][0][1]
        tools.assert_equals(set(['sender', 'request', 'category', 'publishable', 'signal']), set(kwargs.keys()))
        tools.assert_equals(self.category_nested, kwargs['category'])
        tools.assert_equals(self.publishable.__class__, kwargs['sender'])
        tools.assert_equals(self.publishable, kwargs['publishable'])

    def test_object_detail(self):
        response = self.client.get('/nested-category/2008/1/10/first-article/')

        tools.assert_true('category' in response.context)
        tools.assert_equals(self.publishable.category, response.context['category'])

        tools.assert_true('object' in response.context)
        tools.assert_equals(self.publishable, response.context['object'])

        tools.assert_true('content_type' in response.context)
        tools.assert_equals(
                ContentType.objects.get_for_model(self.publishable),
                response.context['content_type']
        )

        tools.assert_true('content_type_name' in response.context)
        tools.assert_equals(
                slugify(self.publishable._meta.verbose_name_plural),
                response.context['content_type_name']
        )

    def test_static_object_detail_redirects_to_correct_url_on_wrong_slug(self):
        self.publishable.static = True
        self.publishable.save()
        response = self.client.get('/nested-category/%d-not-the-first-article/' % self.publishable.id)

        tools.assert_equals(301, response.status_code)
        tools.assert_equals(
            'http://testserver/nested-category/%d-first-article/' % self.publishable.id,
            response['Location']
        )

    def test_static_object_detail_redirects_to_correct_url_on_wrong_category(self):
        self.publishable.static = True
        self.publishable.save()
        response = self.client.get('/nested-category/second-nested-category/%d-%s/' % (self.publishable.id, self.publishable.slug))

        tools.assert_equals(301, response.status_code)
        tools.assert_equals(
            'http://testserver/nested-category/%d-first-article/' % self.publishable.id,
            response['Location']
        )

    def test_static_redirects_preserve_custom_url_remainder(self):
        self.publishable.static = True
        self.publishable.save()
        response = self.client.get('/nested-category/second-nested-category/%d-%s/some/custom/url/action/' % (self.publishable.id, self.publishable.slug))

        tools.assert_equals(301, response.status_code)
        tools.assert_equals(
            'http://testserver/nested-category/%d-first-article/some/custom/url/action/' % self.publishable.id,
            response['Location']
        )


    def test_static_object_detail(self):
        self.publishable.static = True
        self.publishable.save()
        response = self.client.get('/nested-category/%d-first-article/' % self.publishable.id)

        tools.assert_true('category' in response.context)
        tools.assert_equals(self.publishable.category, response.context['category'])

        tools.assert_true('object' in response.context)
        tools.assert_equals(self.publishable, response.context['object'])

        tools.assert_true('content_type' in response.context)
        tools.assert_equals(
                ContentType.objects.get_for_model(self.publishable),
                response.context['content_type']
        )

        tools.assert_true('content_type_name' in response.context)
        tools.assert_equals(
                slugify(self.publishable._meta.verbose_name_plural),
                response.context['content_type_name']
        )

    def test_multiple_same_publications_can_live_while_not_published(self):
        self.publishable.published = True
        self.publishable.save()
        orig_publishable = self.publishable
        create_and_place_a_publishable(self, published=False)
        self.client.get('/nested-category/%d-first-article/' % orig_publishable.id)


class TestGetTemplates(ViewsTestCase):
    def test_homepage_uses_only_path(self):
        tools.assert_equals(
            [u'page/category/ni-hao-category/category.html', u'page/category.html'],
            get_templates('category.html', category=self.category)
        )

    def test_first_nested_uses_only_path(self):
        tools.assert_equals(
            [u'page/category/nested-category/category.html', u'page/category.html'],
            get_templates('category.html', category=self.category_nested)
        )

    def test_more_nested_uses_fallback_to_parents(self):
        tools.assert_equals(
            [u'page/category/nested-category/second-nested-category/category.html', u'page/category/nested-category/category.html', u'page/category.html'],
            get_templates('category.html', category=self.category_nested_second)
        )
