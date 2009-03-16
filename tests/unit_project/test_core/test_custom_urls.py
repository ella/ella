# -*- coding: utf-8 -*-
from djangosanetesting import UnitTestCase

from django.http import Http404

from ella.core.custom_urls import DetailDispatcher

# dummy functions to register as views
def view(request, bits, context):
    return request, bits, context

def custom_view(request, context):
    return request, context


class TestCustomUrlsDispatcher(UnitTestCase):
    def setUp(self):
        super(TestCustomUrlsDispatcher, self).setUp()
        self.dispatcher = DetailDispatcher()

        self.context = {'object': self}
        self.request = object()

    def test_no_extension(self):
        self.assert_raises(Http404, self.dispatcher._get_view, 'start', self)

    def test_register_global_extension(self):
        self.dispatcher.register('start', view)
        self.assert_equals(view, self.dispatcher._get_view('start', self))

    def test_register_extension_for_model(self):
        self.dispatcher.register('another_start', view, model=self.__class__)
        self.assert_equals(view, self.dispatcher._get_view('another_start', self.__class__))

    def test_register_extension_for_model_not_work_for_other_models(self):
        self.dispatcher.register('start', view, model=self.__class__)
        self.assert_raises(Http404, self.dispatcher._get_view, 'start', object())

    def test_no_custom_view(self):
        self.assert_raises(Http404, self.dispatcher._get_custom_detail_view, self.__class__)

    def test_register_custom_view(self):
        self.dispatcher.register_custom_detail(self.__class__, custom_view)
        self.assert_equals(custom_view, self.dispatcher._get_custom_detail_view(self.__class__))

