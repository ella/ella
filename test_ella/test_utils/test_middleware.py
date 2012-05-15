from unittest import TestCase

from django.test.client import RequestFactory

from ella.utils.middleware import LegacyRedirectMiddleware

from nose import tools

class DummyResponse(object):
    def __init__(self, status):
        self.status_code = status

class TestLegacyRedirectMiddleware(TestCase):
    def setUp(self):
        self.rf = RequestFactory()
        self.m = LegacyRedirectMiddleware()
        super(TestLegacyRedirectMiddleware, self).setUp()

    def test_middleware_ignores_non_404_responses(self):
        request = self.rf.get('/articles/10-w-t-f/')
        response = DummyResponse(200)
        tools.assert_true(response is self.m.process_response(request, response))

    def test_middleware_ignores_valid_404_responses(self):
        request = self.rf.get('/this/url/does/not/exist/')
        response = DummyResponse(404)
        tools.assert_true(response is self.m.process_response(request, response))

    def test_middleware_redirects_static_home(self):
        request = self.rf.get('/articles/10-w-t-f/')
        response = DummyResponse(404)
        new_response = self.m.process_response(request, response)
        tools.assert_equals(301, new_response.status_code)
        tools.assert_equals('/10-w-t-f/', new_response['Location'])

    def test_middleware_redirects_static_in_cat(self):
        request = self.rf.get('/nested-category/articles/10-w-t-f/')
        response = DummyResponse(404)
        new_response = self.m.process_response(request, response)
        tools.assert_equals(301, new_response.status_code)
        tools.assert_equals('/nested-category/10-w-t-f/', new_response['Location'])

    def test_middleware_redirects_static_in_cat_name_as_ct(self):
        request = self.rf.get('/articles/articles/10-w-t-f/')
        response = DummyResponse(404)
        new_response = self.m.process_response(request, response)
        tools.assert_equals(301, new_response.status_code)
        tools.assert_equals('/articles/10-w-t-f/', new_response['Location'])

    def test_middleware_redirects_static_with_custom_urls(self):
        request = self.rf.get('/articles/articles/10-w-t-f/comments/add/')
        response = DummyResponse(404)
        new_response = self.m.process_response(request, response)
        tools.assert_equals(301, new_response.status_code)
        tools.assert_equals('/articles/10-w-t-f/comments/add/', new_response['Location'])

    def test_middleware_redirects_non_static_with_custom_urls(self):
        request = self.rf.get('/nested/articles/2010/10/10/articles/w-t-f/comments/add/')
        response = DummyResponse(404)
        new_response = self.m.process_response(request, response)
        tools.assert_equals(301, new_response.status_code)
        tools.assert_equals('/nested/articles/2010/10/10/w-t-f/comments/add/', new_response['Location'])

