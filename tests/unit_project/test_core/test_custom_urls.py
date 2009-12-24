# -*- coding: utf-8 -*-
from copy import deepcopy

from djangosanetesting import UnitTestCase, DatabaseTestCase

from django.http import Http404, HttpResponse

from ella.core.custom_urls import DetailDispatcher
from ella.core import custom_urls

from unit_project.test_core import create_basic_categories, create_and_place_a_publishable
from unit_project import template_loader

# dummy functions to register as views
def view(request, bits, context):
    return u"OK"

def second_view(request, bits, context):
    return request, bits, context

def custom_view(request, context):
    return u"OK"

class TestObjectDetail(DatabaseTestCase):
    def setUp(self):
        super(TestObjectDetail, self).setUp()
        create_basic_categories(self)
        create_and_place_a_publishable(self)
        self.url = self.publishable.get_absolute_url()
        self.old_dispatcher = deepcopy(custom_urls.dispatcher)

    def tearDown(self):
        super(TestObjectDetail, self).tearDown()
        template_loader.templates = {}
        custom_urls.dispatcher = self.old_dispatcher

    def test_custom_detail_view_called_when_registered(self):
        def my_custom_view(request, context):
            return HttpResponse('OK')

        custom_urls.dispatcher.register_custom_detail(self.publishable.__class__, my_custom_view)

        response = self.client.get(self.url)
        self.assert_equals(200, response.status_code)
        self.assert_equals('OK', response.content)

    def test_404_returned_when_view_not_registered(self):
        template_loader.templates['404.html'] = ''
        response = self.client.get(self.url + 'start/')
        self.assert_equals(404, response.status_code)

    def test_custom_view_called_when_registered(self):
        def my_view(request, bits, context):
            return HttpResponse('OK' + ':'.join(bits))
        custom_urls.dispatcher.register('start', my_view)
        response = self.client.get(self.url + 'start/')
        self.assert_equals(200, response.status_code)
        self.assert_equals('OK', response.content)

    def test_custom_view_called_when_registered_and_bits_are_passed_in(self):
        def my_view(request, bits, context):
            return HttpResponse('OK' + ':'.join(bits))
        custom_urls.dispatcher.register('start', my_view)
        response = self.client.get(self.url + 'start/some/more/bits/')
        self.assert_equals(200, response.status_code)
        self.assert_equals('OKsome:more:bits', response.content)


class CustomUrlDispatcherTestCase(UnitTestCase):
    def setUp(self):
        super(CustomUrlDispatcherTestCase, self).setUp()
        self.dispatcher = DetailDispatcher()

        self.context = {'object': self}
        self.request = object()

class TestViewRegistrationRegistration(CustomUrlDispatcherTestCase):

    def test_404_raised_when_view_not_registered(self):
        self.assert_raises(Http404, self.dispatcher._get_view, 'start', self)

    def test_global_extension(self):
        self.dispatcher.register('start', view)
        self.assert_equals(view, self.dispatcher._get_view('start', self))

    def test_bound_for_model(self):
        self.dispatcher.register('start', view, model=self.__class__)
        self.assert_equals(view, self.dispatcher._get_view('start', self.__class__))

    def test_extension_for_model_not_work_for_other_models(self):
        self.dispatcher.register('start', view, model=self.__class__)
        self.assert_raises(Http404, self.dispatcher._get_view, 'start', object())

    def test_cannot_register_same_extension_points_multiple_times(self):
        self.dispatcher.register('start', view)
        self.assert_raises(AssertionError, self.dispatcher.register, 'start', view)

    def test_cannot_register_same_model_extension_points_multiple_times(self):
        self.dispatcher.register('start', view, model=self.__class__)
        self.assert_raises(AssertionError, self.dispatcher.register, 'start', view, model=self.__class__)

    def test_model_extension_has_preference_over_generic_one(self):
        self.dispatcher.register('start', view)
        self.dispatcher.register('start', second_view, model=self.__class__)
        self.assert_equals(second_view, self.dispatcher._get_view('start', self.__class__))


class TestCustomDetailRegistration(CustomUrlDispatcherTestCase):
    def test_no_view_available_without_registration(self):
        self.assert_raises(Http404, self.dispatcher._get_custom_detail_view, self.__class__)

    def test_registration_success(self):
        self.dispatcher.register_custom_detail(self.__class__, custom_view)
        self.assert_equals(custom_view, self.dispatcher._get_custom_detail_view(self.__class__))

class TestViewCalling(CustomUrlDispatcherTestCase):
    def test_nonexisting_view_raises_404(self):
        self.assert_raises(Http404, self.dispatcher.call_view, request=object(), bits=['start'], context=self.context)

    def test_call_custom_detail_simple_success(self):
        self.dispatcher.register_custom_detail(self.__class__, custom_view)
        self.assert_equals(u"OK", self.dispatcher.call_custom_detail(request=object(), context=self.context))

    def test_call_view_simple_success(self):
        self.dispatcher.register('start', view)
        self.assert_equals(u"OK", self.dispatcher.call_view(request=object(), bits=['start'], context=self.context))


from django.conf.urls.defaults import patterns, url

from ella.core.custom_urls import CustomURLResolver
from django.core.urlresolvers import NoReverseMatch

# test views
def dummy_view(request, *args, **kwargs):
    return HttpResponse('dummy_view:%r,%r' % (args, kwargs))

def dummy_view(request, *args, **kwargs):
    return HttpResponse('dummy_view:%r,%r' % (args, kwargs))

class CustomObjectDetailTestCase(DatabaseTestCase):
    urlpatterns = patterns('',
        url(r'^$', dummy_view, {'kwarg_from_patterns': 42}, name='start'),
        url(r'^new/(\d+)/$', dummy_view, name='start-new'),
        url(r'^add/(?P<kwarg_from_url>\d+)/$', dummy_view, name='start-add'),
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


class TestCustomObjectDetailResolver(CustomObjectDetailTestCase):
    def test_resolves_empty_url(self):
        custom_urls.resolver.register('start', self.urlpatterns)

        view, args, kwargs = custom_urls.resolver.resolve(self.publishable, 'start/')
        self.assert_equals(dummy_view, view)
        self.assert_equals((), args)
        self.assert_equals({'kwarg_from_patterns': 42}, kwargs)


    def test_resolves_url_with_arg(self):
        custom_urls.resolver.register('start', self.urlpatterns)

        view, args, kwargs = custom_urls.resolver.resolve(self.publishable, 'start/new/43/')
        self.assert_equals(dummy_view, view)
        self.assert_equals(('43',), args)
        self.assert_equals({}, kwargs)


    def test_resolves_url_with_kwarg(self):
        custom_urls.resolver.register('start', self.urlpatterns)

        view, args, kwargs = custom_urls.resolver.resolve(self.publishable, 'start/add/44/')
        self.assert_equals(dummy_view, view)
        self.assert_equals((), args)
        self.assert_equals({'kwarg_from_url': '44'}, kwargs)


    def test_raises_404_for_incorrect_url(self):
        custom_urls.resolver.register('start', self.urlpatterns)

        self.assert_raises(Http404, custom_urls.resolver.resolve, self.publishable, 'not-start/')

    def test_resolves_url_registered_for_one_model(self):
        custom_urls.resolver.register('start', self.urlpatterns, self.publishable.__class__)

        view, args, kwargs = custom_urls.resolver.resolve(self.publishable, 'start/')
        self.assert_equals(dummy_view, view)
        self.assert_equals((), args)
        self.assert_equals({'kwarg_from_patterns': 42}, kwargs)

    def test_raises_404_for_url_registered_for_different_model_only(self):
        custom_urls.resolver.register('start', self.urlpatterns, self.category.__class__)

        self.assert_raises(Http404, custom_urls.resolver.resolve, self.publishable, 'start/')


class TestCustomObjectDetailReverse(CustomObjectDetailTestCase):
    def test_works_without_args(self):
        custom_urls.resolver.register('start', self.urlpatterns)

        self.assert_equals(self.url + 'start/', custom_urls.resolver.reverse(self.publishable, 'start'))

    def test_works_with_args(self):
        custom_urls.resolver.register('start', self.urlpatterns)

        self.assert_equals(self.url + 'start/new/41/', custom_urls.resolver.reverse(self.publishable, 'start-new', 41))

    def test_works_with_kwargs(self):
        custom_urls.resolver.register('start', self.urlpatterns)

        self.assert_equals(self.url + 'start/add/42/', custom_urls.resolver.reverse(self.publishable, 'start-add', kwarg_from_url=42))

    def test_works_if_registered_for_one_model(self):
        custom_urls.resolver.register('start', self.urlpatterns, self.publishable.__class__)

        self.assert_equals(self.url + 'start/', custom_urls.resolver.reverse(self.publishable, 'start'))

    def test_doesnt_find_url_if_registered_for_different_model_only(self):
        custom_urls.resolver.register('start', self.urlpatterns, self.category.__class__)

        self.assert_raises(NoReverseMatch,  custom_urls.resolver.reverse, self.publishable, 'start')

