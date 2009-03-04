# -*- coding: utf-8 -*-
from djangosanetesting import DatabaseTestCase

from django.core.urlresolvers import reverse

from ella.core.models import Category

from unit_project.test_core import create_basic_categories

class TestCategory(DatabaseTestCase):

    def setUp(self):
        super(TestCategory, self).setUp()
        create_basic_categories(self)

    def test_proper_root_path(self):
        self.assert_equals("", self.category.tree_path)

    def test_proper_firstlevel_path(self):
        self.assert_equals("nested-category", self.category_nested.tree_path)

    def test_category_rename_tree_path(self):
        self.category_nested.slug = u"new-nested-category"
        self.category_nested.save()
        self.assert_equals("new-nested-category", self.category_nested.tree_path)

    def test_proper_secondlevel_path(self):
        self.assert_equals(u"nested-category/second-nested-category", self.category_nested_second.tree_path)

    def test_category_rename_children(self):
        self.category_nested.slug = u"new-nested-category"
        self.category_nested.save()
        category_nested_second = Category.objects.get(pk=self.category_nested_second.pk)
        self.assert_equals(u"new-nested-category/second-nested-category", category_nested_second.tree_path)

    def test_proper_parent(self):
        self.assert_equals(self.category, self.category_nested.get_tree_parent())

    def test_main_parent_nested_second_level(self):
        self.assert_equals(self.category_nested, self.category_nested_second.main_parent)

    def test_main_parent_nested(self):
        self.assert_equals(self.category_nested, self.category_nested.main_parent)

    def test_main_parent_nested_third(self):
        category_nested_third = Category.objects.create(
            title=u"Third nested category",
            description=u"category nested in self.category_nested_second",
            tree_parent=self.category_nested_second,
            site_id = self.site_id,
            slug=u"third-nested-category",
        )
        self.assert_equals(self.category_nested, category_nested_third.main_parent)

    def test_root_url(self):
        url = reverse('root_homepage')
        self.assert_equals(url, self.category.get_absolute_url())

    def test_category_url(self):
        url = reverse('category_detail', args=(self.category_nested.tree_path, ))
        self.assert_equals(url, self.category_nested.get_absolute_url())

