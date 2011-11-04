# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.test.client import RequestFactory

from djangosanetesting import DatabaseTestCase

from ella.ellatagging.views import TaggedPublishablesView
from ella.articles.models import Article
from ella.core.models import Placement, Publishable

from unit_project.test_core import (create_basic_categories,
                                    create_and_place_a_publishable)
from unit_project import template_loader
from datetime import datetime

class TestTaggingPagination(DatabaseTestCase):
    """Tests depends on setttings TAG_LISTINGS_PAGINATE_BY = 1"""
    def setUp(self):
        try:
            import tagging
        except ImportError, e:
            raise self.SkipTest()

        from tagging.models import Tag, TaggedItem
        if not TaggedItem._meta.installed:
            raise self.SkipTest()
        super(TestTaggingPagination, self).setUp()
        create_basic_categories(self)
        create_and_place_a_publishable(self)
        self.factory = RequestFactory()

        self.pub = Article.objects.create(
            title=u'Paggination',
            slug=u'paggination',
            description=u'Testing paggination',
            category=self.category_nested
            )

        self.only_pub = Publishable.objects.get(pk=self.pub.pk)
        self.place = Placement.objects.create(
            publishable=self.pub,
            category=self.category_nested,
            publish_from=datetime(2008, 1, 20)
            )
        Tag.objects.update_tags(self.only_pub, 'tag1')
        Tag.objects.update_tags(self.only_publishable, 'tag1')
        self.tag = Tag.objects.get(name='tag1')

    def tearDown(self):
        super(TestTaggingPagination, self).tearDown()

    def test_tagged_paggination_view_without_page_parameter(self):
        url = reverse('tag_list', kwargs={'tag': 'tag1'})
        request = self.factory.get(url)
        tpv = TaggedPublishablesView.as_view()
        response = tpv(request, tag='tag1')
        self.assert_true(200, response.status_code)
        self.assert_true(response.context_data['is_paginated'])
        self.assert_equals(1, response.context_data['results_per_page'])
        self.assert_equals(self.tag, response.context_data['tag'])
        self.assert_equals(1, len(response.context_data['object_list']))
        self.assert_equals(self.only_publishable,
                           response.context_data['object_list'][0])


    def test_tagged_paggination_view_with_page1_parameter(self):
        url = reverse('tag_list', kwargs={'tag': 'tag1'})
        request = self.factory.get(url, {'p': 1})
        tpv = TaggedPublishablesView.as_view()
        response = tpv(request, tag='tag1')
        self.assert_true(200, response.status_code)
        self.assert_true(response.context_data['is_paginated'])
        self.assert_equals(1, response.context_data['results_per_page'])
        self.assert_equals(self.tag, response.context_data['tag'])
        self.assert_equals(1, len(response.context_data['object_list']))
        self.assert_equals(self.only_publishable,
                           response.context_data['object_list'][0])


    def test_tagged_paggination_view_with_page2_parameter(self):
        url = reverse('tag_list', kwargs={'tag': 'tag1'})
        request = self.factory.get(url, {'p': 2})
        tpv = TaggedPublishablesView.as_view()
        response = tpv(request, tag='tag1')
        self.assert_true(200, response.status_code)
        self.assert_true(response.context_data['is_paginated'])
        self.assert_equals(1, response.context_data['results_per_page'])
        self.assert_equals(self.tag, response.context_data['tag'])
        self.assert_equals(1, len(response.context_data['object_list']))
        self.assert_equals(self.only_pub,
                           response.context_data['object_list'][0])
