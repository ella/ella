# -*- coding: utf-8 -*-
from unittest import TestCase as UnitTestCase
from test_ella.cases import RedisTestCase as TestCase

from nose import tools

from django.http import Http404
from django.db.models import get_models
from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import slugify

from ella.core.views import ObjectDetail, get_content_type, ListContentType
from ella.core.models import Listing, Publishable

from test_ella.test_core import create_basic_categories, create_and_place_a_publishable, \
        create_and_place_more_publishables, list_all_publishables_in_category_by_hour

class ViewHelpersTestCase(TestCase):
    def setUp(self):
        super(ViewHelpersTestCase, self).setUp()
        create_basic_categories(self)
        create_and_place_a_publishable(self)

        # mock user
        self.user = self
        setattr(self.user, 'is_staff', False)

        # mock request
        self.request = self
        setattr(self.user, 'GET', {})

class TestGetContentType(UnitTestCase):
    def test_by_brute_force(self):
        for m in get_models():
            if issubclass(m, Publishable):
                ct = ContentType.objects.get_for_model(m)
                tools.assert_equals(ct, get_content_type(slugify(m._meta.verbose_name_plural)))

    def test_raises_404_on_non_existing_model(self):
        tools.assert_raises(Http404, get_content_type, '')

class TestCategoryDetail(ViewHelpersTestCase):
    def setUp(self):
        super(TestCategoryDetail, self).setUp()
        self.category_detail = ListContentType()

    def test_returns_category_by_tree_path(self):
        cat = self.category_detail.get_category(self.request, 'nested-category')
        c = self.category_detail.get_context(self.request, cat)
        tools.assert_equals(self.category_nested, c['category'])
        tools.assert_false(c['is_homepage'])

    def test_returns_home_page_with_no_args(self):
        cat = self.category_detail.get_category(self.request, '')
        c = self.category_detail.get_context(self.request, cat)
        tools.assert_equals(self.category, c['category'])
        tools.assert_true(c['is_homepage'])

    def test_returns_nested_category_by_tree_path(self):
        cat = self.category_detail.get_category(self.request, 'nested-category/second-nested-category')
        c = self.category_detail.get_context(self.request, cat)
        tools.assert_equals(self.category_nested_second, c['category'])
        tools.assert_false(c['is_homepage'])

class TestObjectDetail(ViewHelpersTestCase):
    def setUp(self):
        super(TestObjectDetail, self).setUp()
        self.correct_args = [self.request, 'nested-category', 'first-article', '2008', '1', '10', None]
        self.correct_static_args = self.correct_args[:3] + [None, None, None, self.publishable.id]
        self.object_detail = ObjectDetail()

    def test_raises_404_on_incorrect_category(self):
        self.correct_args[1] = 'not-an-existing-category'
        tools.assert_raises(Http404, self.object_detail.get_context, *self.correct_args)

    def test_raises_404_on_wrong_category(self):
        self.correct_args[1] = ''
        tools.assert_raises(Http404, self.object_detail.get_context, *self.correct_args)

    def test_raises_404_on_incorrect_slug(self):
        self.correct_args[2] = 'not-an-existing-slug'
        tools.assert_raises(Http404, self.object_detail.get_context, *self.correct_args)

    def test_raises_404_on_incorrect_date(self):
        self.correct_args[3] = '2000'
        tools.assert_raises(Http404, self.object_detail.get_context, *self.correct_args)

    def test_returns_correct_context(self):
        c = self.object_detail.get_context(*self.correct_args)

        tools.assert_equals(4, len(c.keys()))
        tools.assert_equals(self.publishable, c['object'])
        tools.assert_equals(self.category_nested, c['category'])
        tools.assert_equals('articles', c['content_type_name'])
        tools.assert_equals(self.publishable.content_type, c['content_type'])

    def test_doesnt_match_static_placement_if_date_is_supplied(self):
        self.publishable.static = True
        self.publishable.save()
        tools.assert_raises(Http404, self.object_detail.get_context, *self.correct_args)

    def test_doesnt_match_placement_if_date_is_not_supplied(self):
        self.correct_args = self.correct_args[:3] + [None, None, None, None]
        tools.assert_raises(Http404, self.object_detail.get_context, *self.correct_args)

    def test_matches_static_placement_if_date_is_not_supplied(self):
        self.publishable.static = True
        self.publishable.save()

        c = self.object_detail.get_context(*self.correct_static_args)

        tools.assert_equals(4, len(c.keys()))
        tools.assert_equals(self.publishable, c['object'])
        tools.assert_equals(self.category_nested, c['category'])
        tools.assert_equals('articles', c['content_type_name'])
        tools.assert_equals(self.publishable.content_type, c['content_type'])

    def test_raises_wrong_url_on_missing_category(self):
        self.publishable.static = True
        self.publishable.save()

        self.correct_static_args[1] = 'non-existent/category'
        tools.assert_raises(self.object_detail.WrongUrl, self.object_detail.get_context, *self.correct_static_args)

    def test_raises_wrong_url_on_wong_slug(self):
        self.publishable.static = True
        self.publishable.save()

        self.correct_static_args[2] = 'not a slug'
        tools.assert_raises(self.object_detail.WrongUrl, self.object_detail.get_context, *self.correct_static_args)

    def test_raises_wrong_url_on_not_static(self):
        tools.assert_raises(self.object_detail.WrongUrl, self.object_detail.get_context, *self.correct_static_args)

    def test_raises_wrong_url_on_wong_category(self):
        self.publishable.static = True
        self.publishable.save()

        self.correct_static_args[1] = ''
        tools.assert_raises(self.object_detail.WrongUrl, self.object_detail.get_context, *self.correct_static_args)

class TestListContentType(ViewHelpersTestCase):
    def setUp(self):
        super(TestListContentType, self).setUp()
        create_and_place_more_publishables(self)
        list_all_publishables_in_category_by_hour(self, category=self.category)
        self.list_content_type = ListContentType()

    def test_only_category_and_year_returns_all_listings(self):
        c = self.list_content_type.get_context(self.request, self.category, '2008')
        tools.assert_equals(self.listings, list(c['listings']))

    def test_only_nested_category_and_year_returns_all_listings(self):
        Listing.objects.all().update(category=self.category_nested_second)
        c = self.list_content_type.get_context(self.request, self.category_nested_second, '2008')
        tools.assert_equals(self.listings, list(c['listings']))

    def test_return_first_2_listings_if_paginate_by_2(self):
        self.category.app_data = {'ella': {'paginate_by': 2, 'first_page_count': 2}}
        self.category.save()
        c = self.list_content_type.get_context(self.request, self.category, '2008')
        tools.assert_equals(self.listings[:2], list(c['listings']))
        tools.assert_true(c['is_paginated'])

    def test_return_second_2_listings_if_paginate_by_2_and_page_2(self):
        self.category.app_data = {'ella': {'paginate_by': 2, 'first_page_count': 2}}
        self.category.save()
        self.request.GET['p'] = '2'
        c = self.list_content_type.get_context(self.request, self.category, '2008')
        tools.assert_equals(self.listings[2:4], list(c['listings']))
        tools.assert_true(c['is_paginated'])

    def test_returns_empty_list_if_no_listing_found(self):
        c = self.list_content_type.get_context(self.request, self.category, '2007')
        tools.assert_equals([], list(c['listings']))

    def test_raises404_for_incorrect_page(self):
        self.request.GET['p'] = '200'
        tools.assert_raises(Http404, self.list_content_type.get_context, self.request, self.category, '2008')

    def test_raises404_for_incorrect_category(self):
        tools.assert_raises(Http404, self.list_content_type.get_category, self.request, 'XXX')

    def test_raises404_for_incorrect_month(self):
        tools.assert_raises(Http404, self.list_content_type.get_context, self.request, self.category, '2008', '13')

    def test_raises404_for_incorrect_day(self):
        tools.assert_raises(Http404, self.list_content_type.get_context, self.request, self.category, '2008', '1', '42')

    def test_raises404_for_incorrect_date(self):
        tools.assert_raises(Http404, self.list_content_type.get_context, self.request, self.category, '2008', '2', '30')


