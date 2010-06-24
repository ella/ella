# -*- coding: utf-8 -*-
from datetime import datetime
from djangosanetesting import DatabaseTestCase

from django.contrib.sites.models import Site
from django.contrib.redirects.models import Redirect

from ella.core.models import Placement, Category
from ella.articles.models import Article

from unit_project.test_core import create_basic_categories, create_and_place_a_publishable

class TestPlacement(DatabaseTestCase):

    def setUp(self):
        super(TestPlacement, self).setUp()
        create_basic_categories(self)
        create_and_place_a_publishable(self)

    def test_home_url(self):
        self.placement.category = self.category
        self.placement.save()
        self.assert_equals('/2008/1/10/articles/first-article/', self.placement.get_absolute_url())

    def test_url(self):
        self.assert_equals('/nested-category/2008/1/10/articles/first-article/', self.placement.get_absolute_url())

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
        
        p = Placement.objects.create(
            publishable=self.publishable,
            category=category,
            publish_from=datetime(2008,1,10)
        )

        self.assert_equals(u'http://not-example.com/2008/1/10/articles/first-article/', p.get_absolute_url())

    def test_duplicity(self):
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
            publishable=self.publishable,
            category=category,
            publish_from=datetime(2008,1,10)
        )
        publishable_two = Article.objects.create(
            title=u'First Article',
            slug=u'first-article',
            description=u'Some\nlonger\ntext',
            category=category
        )
        raised = False
        try:
            p_two = Placement.objects.create(
                publishable=publishable_two,
                category=category,
                publish_from=datetime(2008,1,10)
            )
        except ValueError:
            raised = True #OK
        self.assert_equals(True, raised) # ValueError should be raised as duplicity check works right way.

    def test_default_slug(self):
        self.assert_equals(self.publishable.slug, self.placement.slug)

    def test_slug_rename(self):
        self.publishable.slug = 'first-article-second-slug'
        self.publishable.save()
        placement = Placement.objects.get(pk=self.placement.pk)
        self.assert_equals(self.publishable.slug, placement.slug)

    def test_custom_slug(self):
        self.placement.slug = 'old-article-new-slug'
        self.placement.save()
        self.assert_equals('/nested-category/2008/1/10/articles/old-article-new-slug/', self.placement.get_absolute_url())

    def test_custom_slug_rename(self):
        self.placement.slug = 'old-article-new-slug'
        self.placement.save()
        self.publishable.slug = 'first-article-second-slug'
        self.publishable.save()
        self.assert_equals('/nested-category/2008/1/10/articles/old-article-new-slug/', self.placement.get_absolute_url())

    
class TestRedirects(DatabaseTestCase):

    def setUp(self):
        super(TestRedirects, self).setUp()
        create_basic_categories(self)
        create_and_place_a_publishable(self)

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

    def test_ability_to_place_back_and_forth(self):
        self.placement.slug = 'old-article-new-slug'
        self.placement.save()
        self.placement.slug = 'first-article'
        self.placement.save()
        self.placement.slug = 'old-article-new-slug'
        self.placement.save()


