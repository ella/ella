# -*- coding: utf-8 -*-
from datetime import datetime
from djangosanetesting import DatabaseTestCase

from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from ella.core.models import Placement, Category
# choose Article as an example publishable, we cannot use Publishable directly
# because it's abstract
from ella.articles.models import Article

class TestPublishable(DatabaseTestCase):

    def setUp(self):
        super(TestPublishable, self).setUp()

        self.site_id = getattr(settings, "SITE_ID", 1)

        self.category = Category.objects.create(
            title=u"你好 category",
            description=u"example testing category",
            site_id=self.site_id,
            slug=u"ni-hao-category",
        )

        self.category_nested = Category.objects.create(
            title=u"nested category",
            description=u"category nested in self.category",
            tree_parent=self.category,
            site_id=self.site_id,
            slug=u"nested-category",
        )

        self.publishable = Article.objects.create(
            title=u'First Article',
            slug=u'first-article',
            perex=u'Some\nlonger\ntext',
            category=self.category_nested
        )

        self.article_ct = ContentType.objects.get_for_model(Article)

        self.placement = Placement.objects.create(
            target_ct=self.article_ct,
            target_id=self.publishable.pk,
            category=self.category_nested,
            publish_from=datetime(2008,1,10)
        )

    def test_url(self):
        self.assert_equals('/nested-category/2008/1/10/articles/first-article/', self.publishable.get_absolute_url())

    def test_domain_url(self):
        self.assert_equals('http://example.com/nested-category/2008/1/10/articles/first-article/', self.publishable.get_domain_url())

    def test_main_placement_with_single_placement(self):
        self.assert_equals(self.publishable.main_placement, self.placement)

    def test_main_placement_with_single_placement_on_other_site(self):
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

        self.placement.category = category
        self.placement.save()
        
        self.assert_equals(None, self.publishable.main_placement)

    def test_main_placement_with_two_placements_on_one_site(self):
        p = Placement.objects.create(
            target_ct=self.article_ct,
            target_id=self.publishable.pk,
            category=self.category,
            publish_from=datetime(2008,1,10)
        )
        self.assert_equals(self.publishable.main_placement, self.placement)

    def test_main_placement_with_two_placements_on_two_sites(self):
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
        
        p = Placement.objects.create(
            target_ct=self.article_ct,
            target_id=self.publishable.pk,
            category=category,
            publish_from=datetime(2008,1,10)
        )

        self.assert_equals(self.publishable.main_placement, self.placement)

