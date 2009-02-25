# -*- coding: utf-8 -*-
from djangosanetesting import DatabaseTestCase

from django.conf import settings

from ella.core.models import Category

class TestCategory(DatabaseTestCase):

    def setUp(self):
        super(TestCategory, self).setUp()

        self.site_id = getattr(settings, "SITE_ID", 1)

        self.category = Category.objects.create(
            title=u"你好 category",
            description=u"exmple testing category",
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

    def test_proper_root_path(self):
        self.assert_equals("", self.category.tree_path)

    def test_proper_firstlevel_path(self):
        self.assert_equals("nested-category", self.category_nested.tree_path)

    def test_proper_secondlevel_path(self):
        category_nested_second = Category.objects.create(
            title=u" second nested category",
            description=u"category nested in self.category_nested",
            tree_parent=self.category_nested,
            site_id = self.site_id,
            slug=u"second-nested-category",
        )

        self.assert_equals(u"nested-category/second-nested-category", category_nested_second.tree_path)

    def test_proper_parent(self):
        self.assert_equals(self.category, self.category_nested.get_tree_parent())

