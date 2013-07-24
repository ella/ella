# -*- coding: utf-8 -*-

from unittest import TestCase as UnitTestCase
from test_ella.cases import RedisTestCase as TestCase

from nose import tools

from django.http import Http404, HttpResponse
from django.core.urlresolvers import NoReverseMatch
from django.template import Template, Context

try:
    from django.conf.urls import patterns, url
except ImportError:
    from django.conf.urls.defaults import patterns, url

from ella.core.custom_urls import CustomURLResolver
from ella.core import custom_urls
from ella.core.models import Category

from test_ella.test_core import create_basic_categories, create_and_place_a_publishable
from test_ella import template_loader

# dummy functions to register as views
def view(request, bits, context):
    return u"OK"

def second_view(request, bits, context):
    return request, bits, context

def custom_view(request, context):
    return u"OK"

def dummy_view(request, *args, **kwargs):
    return HttpResponse('dummy_view:%r,%r' % (args, kwargs))


class CustomObjectDetailTestCase(TestCase):
    urlpatterns = patterns('',
        url(r'^$', dummy_view, {'kwarg_from_patterns': 42}, name='prefix'),
        url(r'^new/(\d+)/$', dummy_view, name='prefix-new'),
        url(r'^add/(?P<kwarg_from_url>\d+)/$', dummy_view, name='prefix-add'),
    )

    def setUp(self):
        super(CustomObjectDetailTestCase, self).setUp()
        create_basic_categories(self)
        create_and_place_a_publishable(self)

        self.url = self.publishable.get_absolute_url()
        self.old_resolver = custom_urls.resolver
        custom_urls.resolver = CustomURLResolver()

    def tearDown(self):
        super(CustomObjectDetailTestCase, self).tearDown()
        template_loader.templates = {}
        custom_urls.resolver = self.old_resolver

class TestCustomURLTemplateTag(CustomObjectDetailTestCase):
    def test_view_with_no_args_resolves(self):
        custom_urls.resolver.register(self.urlpatterns, prefix='prefix')
        t = Template('{% load custom_urls_tags %}{% custom_url object prefix %}')

        tools.assert_equals(self.url + 'prefix/', t.render(Context({'object': self.publishable})))

    def test_view_with_args_resolves(self):
        custom_urls.resolver.register(self.urlpatterns, prefix='prefix')
        t = Template('{% load custom_urls_tags %}{% custom_url object prefix-new some_id %}')

        tools.assert_equals(self.url + 'prefix/new/44/', t.render(Context({'object': self.publishable, 'some_id': 44})))

    def test_view_with_kwargs_resolves(self):
        custom_urls.resolver.register(self.urlpatterns, prefix='prefix')
        t = Template('{% load custom_urls_tags %}{% custom_url object prefix-add kwarg_from_url=12 %}')

        tools.assert_equals(self.url + 'prefix/add/12/', t.render(Context({'object': self.publishable})))


class TestObjectDetail(CustomObjectDetailTestCase):
    def test_categories_can_also_have_custom_defail(self):
        def my_custom_view(request, context):
            return HttpResponse('OK')

        custom_urls.resolver.register_custom_detail(Category, my_custom_view)

        response = self.client.get('/')
        tools.assert_equals(200, response.status_code)
        tools.assert_equals('OK', response.content)

    def test_custom_detail_view_called_when_registered(self):
        def my_custom_view(request, context):
            return HttpResponse('OK')

        custom_urls.resolver.register_custom_detail(self.publishable.__class__, my_custom_view)

        response = self.client.get(self.url)
        tools.assert_equals(200, response.status_code)
        tools.assert_equals('OK', response.content)

    def test_404_returned_when_view_not_registered(self):
        template_loader.templates['404.html'] = ''
        response = self.client.get(self.url + 'prefix/')
        tools.assert_equals(404, response.status_code)

    def test_custom_view_called_when_registered(self):
        custom_urls.resolver.register(self.urlpatterns, prefix='prefix')

        response = self.client.get(self.url + 'prefix/')
        tools.assert_equals(200, response.status_code)

    def test_custom_view_called_when_registered_witth_args(self):
        custom_urls.resolver.register(self.urlpatterns, prefix='prefix')

        response = self.client.get(self.url + 'prefix/add/41/')
        tools.assert_equals(200, response.status_code)


class TestCustomDetailRegistration(UnitTestCase):
    def setUp(self):
        super(TestCustomDetailRegistration, self).setUp()

        self.context = {'object': self}
        self.request = object()
        self.resolver = CustomURLResolver()

    def test_no_view_available_without_registration(self):
        tools.assert_raises(Http404, self.resolver._get_custom_detail_view, self.__class__)

    def test_registration_success(self):
        self.resolver.register_custom_detail(self.__class__, custom_view)
        tools.assert_equals(custom_view, self.resolver._get_custom_detail_view(self.__class__))

    def test_call_custom_detail_simple_success(self):
        self.resolver.register_custom_detail(self.__class__, custom_view)
        tools.assert_equals(u"OK", self.resolver.call_custom_detail(request=object(), context=self.context))



class TestCustomObjectDetailCallView(CustomObjectDetailTestCase):
    def test_view_with_args_called_correctly(self):
        custom_urls.resolver.register(self.urlpatterns, prefix='prefix')

        response = custom_urls.resolver.call_custom_view(object(), self.publishable, 'prefix/new/42/', {'context': 1})
        tools.assert_equals(200, response.status_code)
        tools.assert_equals("dummy_view:({'context': 1}, '42'),{}", response.content)

    def test_view_with_kwargs_called_correctly(self):
        custom_urls.resolver.register(self.urlpatterns, prefix='prefix')

        response = custom_urls.resolver.call_custom_view(object, self.publishable, 'prefix/add/52/', {'context': 1})
        tools.assert_equals(200, response.status_code)
        tools.assert_equals("dummy_view:({'context': 1},),{'kwarg_from_url': '52'}", response.content)

    def test_view_with_no_args_called_correctly(self):
        custom_urls.resolver.register(self.urlpatterns, prefix='prefix')

        response = custom_urls.resolver.call_custom_view(object, self.publishable, 'prefix/', {'context': 1})
        tools.assert_equals(200, response.status_code)
        tools.assert_equals("dummy_view:({'context': 1},),{'kwarg_from_patterns': 42}", response.content)

    def test_404_raised_for_nonexitant_url(self):
        tools.assert_raises(Http404, custom_urls.resolver.call_custom_view, object(), self.publishable, 'prefix/', {})


class TestCustomObjectDetailResolver(CustomObjectDetailTestCase):
    def test_resolves_empty_url(self):
        custom_urls.resolver.register(self.urlpatterns, prefix='prefix')

        view, args, kwargs = custom_urls.resolver.resolve(self.publishable, 'prefix/')
        tools.assert_equals(dummy_view, view)
        tools.assert_equals((), args)
        tools.assert_equals({'kwarg_from_patterns': 42}, kwargs)


    def test_resolves_url_with_arg(self):
        custom_urls.resolver.register(self.urlpatterns, prefix='prefix')

        view, args, kwargs = custom_urls.resolver.resolve(self.publishable, 'prefix/new/43/')
        tools.assert_equals(dummy_view, view)
        tools.assert_equals(('43',), args)
        tools.assert_equals({}, kwargs)


    def test_resolves_url_with_kwarg(self):
        custom_urls.resolver.register(self.urlpatterns, prefix='prefix')

        view, args, kwargs = custom_urls.resolver.resolve(self.publishable, 'prefix/add/44/')
        tools.assert_equals(dummy_view, view)
        tools.assert_equals((), args)
        tools.assert_equals({'kwarg_from_url': '44'}, kwargs)

    def test_resolves_url_without_start(self):
        custom_urls.resolver.register(self.urlpatterns)

        view, args, kwargs = custom_urls.resolver.resolve(self.publishable, 'add/44/')
        tools.assert_equals(dummy_view, view)
        tools.assert_equals((), args)
        tools.assert_equals({'kwarg_from_url': '44'}, kwargs)


    def test_raises_404_for_incorrect_url(self):
        custom_urls.resolver.register(self.urlpatterns, prefix='prefix')

        tools.assert_raises(Http404, custom_urls.resolver.resolve, self.publishable, 'not-prefix/')

    def test_resolves_url_registered_for_one_model(self):
        custom_urls.resolver.register(self.urlpatterns, prefix='prefix', model=self.publishable.__class__)

        view, args, kwargs = custom_urls.resolver.resolve(self.publishable, 'prefix/')
        tools.assert_equals(dummy_view, view)
        tools.assert_equals((), args)
        tools.assert_equals({'kwarg_from_patterns': 42}, kwargs)

    def test_raises_404_for_url_registered_for_different_model_only(self):
        custom_urls.resolver.register(self.urlpatterns, prefix='prefix', model=self.category.__class__)

        tools.assert_raises(Http404, custom_urls.resolver.resolve, self.publishable, 'prefix/')


class TestCustomObjectDetailReverse(CustomObjectDetailTestCase):
    def test_works_without_args(self):
        custom_urls.resolver.register(self.urlpatterns, prefix='prefix')

        tools.assert_equals(self.url + 'prefix/', custom_urls.resolver.reverse(self.publishable, 'prefix'))

    def test_works_with_args(self):
        custom_urls.resolver.register(self.urlpatterns)

        tools.assert_equals(self.url + 'new/41/', custom_urls.resolver.reverse(self.publishable, 'prefix-new', 41))

    def test_works_with_kwargs(self):
        custom_urls.resolver.register(self.urlpatterns, prefix='prefix')

        tools.assert_equals(self.url + 'prefix/add/42/', custom_urls.resolver.reverse(self.publishable, 'prefix-add', kwarg_from_url=42))

    def test_works_if_registered_for_one_model(self):
        custom_urls.resolver.register(self.urlpatterns, prefix='prefix', model=self.publishable.__class__)

        tools.assert_equals(self.url + 'prefix/', custom_urls.resolver.reverse(self.publishable, 'prefix'))

    def test_doesnt_find_url_if_registered_for_different_model_only(self):
        custom_urls.resolver.register(self.urlpatterns, prefix='prefix', model=self.category.__class__)

        tools.assert_raises(NoReverseMatch,  custom_urls.resolver.reverse, self.publishable, 'prefix')

