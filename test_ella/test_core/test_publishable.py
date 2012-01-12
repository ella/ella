# -*- coding: utf-8 -*-
from django.test import TestCase

from nose import tools

from test_ella.test_core import create_basic_categories, create_and_place_a_publishable

class PublishableTestCase(TestCase):
    def setUp(self):
        super(PublishableTestCase, self).setUp()
        create_basic_categories(self)
        create_and_place_a_publishable(self)


class TestPublishableHelpers(PublishableTestCase):
    def test_url(self):
        tools.assert_equals('/nested-category/2008/1/10/articles/first-article/', self.publishable.get_absolute_url())

    def test_domain_url(self):
        tools.assert_equals('http://example.com/nested-category/2008/1/10/articles/first-article/', self.publishable.get_domain_url())

