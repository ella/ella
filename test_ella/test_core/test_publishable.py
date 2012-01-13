# -*- coding: utf-8 -*-
from datetime import datetime

from django.test import TestCase
from django.contrib.sites.models import Site
from django.contrib.redirects.models import Redirect

from ella.core.models import Category

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

class TestRedirects(TestCase):

    def setUp(self):
        super(TestRedirects, self).setUp()
        create_basic_categories(self)
        create_and_place_a_publishable(self)

    def test_url_change_creates_redirect(self):
        self.publishable.slug = 'old-article-new-slug'
        self.publishable.save()
        tools.assert_equals(1, Redirect.objects.count())
        r = Redirect.objects.all()[0]

        tools.assert_equals('/nested-category/2008/1/10/articles/first-article/', r.old_path)
        tools.assert_equals('/nested-category/2008/1/10/articles/old-article-new-slug/', r.new_path)
        tools.assert_equals(self.site_id, r.site_id)

    def test_url_change_updates_existing_redirects(self):
        r = Redirect.objects.create(site_id=self.site_id, new_path='/nested-category/2008/1/10/articles/first-article/', old_path='some-path')
        self.publishable.slug = 'old-article-new-slug'
        self.publishable.save()
        tools.assert_equals(2, Redirect.objects.count())
        r = Redirect.objects.get(pk=r.pk)

        tools.assert_equals('some-path', r.old_path)
        tools.assert_equals('/nested-category/2008/1/10/articles/old-article-new-slug/', r.new_path)
        tools.assert_equals(self.site_id, r.site_id)

    def test_ability_to_place_back_and_forth(self):
        self.publishable.slug = 'old-article-new-slug'
        self.publishable.save()
        self.publishable.slug = 'first-article'
        self.publishable.save()
        self.publishable.slug = 'old-article-new-slug'
        self.publishable.save()


class TestUrl(TestCase):

    def setUp(self):
        super(TestUrl, self).setUp()
        create_basic_categories(self)
        create_and_place_a_publishable(self)

    def test_home_url(self):
        self.publishable.category = self.category
        self.publishable.save()
        tools.assert_equals('/2008/1/10/articles/first-article/', self.publishable.get_absolute_url())

    def test_url(self):
        tools.assert_equals('/nested-category/2008/1/10/articles/first-article/', self.publishable.get_absolute_url())

    def test_url_on_other_site(self):
        site = Site.objects.create(
            name='some site',
            domain='not-example.com'
        )

        category = Category.objects.create(
            title=u"再见 category",
            description=u"example testing category, second site",
            site=site,
            slug=u'zai-jian-category',
        )

        self.publishable.category = category
        self.publishable.publish_from = datetime(2008,1,10)
        self.publishable.save()

        tools.assert_equals(u'http://not-example.com/2008/1/10/articles/first-article/', self.publishable.get_absolute_url())

