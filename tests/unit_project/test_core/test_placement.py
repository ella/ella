# -*- coding: utf-8 -*-
from datetime import datetime
from djangosanetesting import DatabaseTestCase

from django.contrib.redirects.models import Redirect
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from ella.core.models import Placement, Category
# choose Article as an example publishable, we cannot use Publishable directly
# because it's abstract
from ella.articles.models import Article

class TestPlacement(DatabaseTestCase):

    def setUp(self):
        super(TestPlacement, self).setUp()

        self.site_id = getattr(settings, "SITE_ID", 1)

        self.category = Category.objects.create(
            title=u"你好 category",
            description=u"example testing category",
            site_id = self.site_id,
            slug=u"ni-hao-category",
        )

        self.category_nested = Category.objects.create(
            title=u"nested category",
            description=u"category nested in self.category",
            tree_parent=self.category,
            site_id = self.site_id,
            slug=u"nested-category",
        )

        self.article = Article.objects.create(
            title=u'First Article',
            slug=u'first-article',
            perex=u'Some\nlonger\ntext',
            category=self.category_nested
        )

        self.article_ct = ContentType.objects.get_for_model(Article)

        self.placement = Placement.objects.create(
            target_ct=self.article_ct,
            target_id=self.article.pk,
            category=self.category_nested,
            publish_from=datetime(2008,1,10)
        )

    def test_home_url(self):
        self.placement.category = self.category
        self.placement.save()
        self.assert_equals('/2008/1/10/articles/first-article/', self.placement.get_absolute_url())

    def test_url(self):
        self.assert_equals('/nested-category/2008/1/10/articles/first-article/', self.placement.get_absolute_url())

    def test_default_slug(self):
        self.assert_equals(self.article.slug, self.placement.slug)

    def test_slug_rename(self):
        self.article.slug = 'first-article-second-slug'
        self.article.save()
        placement = Placement.objects.get(pk=self.placement.pk)
        self.assert_equals(self.article.slug, placement.slug)

    def test_custom_slug(self):
        self.placement.slug = 'old-article-new-slug'
        self.placement.save()
        self.assert_equals('/nested-category/2008/1/10/articles/old-article-new-slug/', self.placement.get_absolute_url())

    def test_custom_slug_rename(self):
        self.placement.slug = 'old-article-new-slug'
        self.placement.save()
        self.article.slug = 'first-article-second-slug'
        self.article.save()
        self.assert_equals('/nested-category/2008/1/10/articles/old-article-new-slug/', self.placement.get_absolute_url())

    def test_url_change_creates_redirect(self):
        self.placement.slug = 'old-article-new-slug'
        self.placement.save()
        self.assert_equals(1, Redirect.objects.count())
        r = Redirect.objects.all()[0]
        self.assert_equals('/nested-category/2008/1/10/articles/first-article/', r.old_path)
        self.assert_equals('/nested-category/2008/1/10/articles/old-article-new-slug/', r.new_path)
        self.assert_equals(self.site_id, r.site_id)

    def test_url_change_updates_existing_redirects(self):
        r = Redirect.objects.create(site_id=self.site_id, new_path='/nested-category/2008/1/10/articles/first-article/', old_path='some-path')
        self.placement.slug = 'old-article-new-slug'
        self.placement.save()
        self.assert_equals(2, Redirect.objects.count())
        r = Redirect.objects.get(pk=r.pk)
        self.assert_equals('some-path', r.old_path)
        self.assert_equals('/nested-category/2008/1/10/articles/old-article-new-slug/', r.new_path)
        self.assert_equals(self.site_id, r.site_id)
    
