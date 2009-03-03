# -*- coding: utf-8 -*-
from djangosanetesting import UnitTestCase

from django.contrib.sites.models import Site

from ella.core.models import Category
from ella.core.templatetags.core import _parse_box, BoxNode

class TestBoxTagParser(UnitTestCase):
    def test_parse_box_with_pk(self):
        node = _parse_box([], ['box', 'box_type', 'for', 'core.category', 'with', 'pk', '1'])
        self.assert_true(isinstance(node, BoxNode))
        self.assert_equals('box_type', node.box_type)
        self.assert_equals(Category, node.model)
        self.assert_equals(('pk', '1'), node.lookup)

    def test_parse_box_for_varname(self):
        node = _parse_box([], ['box', 'other_box_type', 'for', 'var_name'])
        self.assert_true(isinstance(node, BoxNode))
        self.assert_equals('other_box_type', node.box_type)
        self.assert_equals('var_name', node.var_name)

    def test_parse_box_with_slug(self):
        node = _parse_box([], ['box', 'box_type', 'for', 'sites.site', 'with', 'slug', '"home"'])
        self.assert_true(isinstance(node, BoxNode))
        self.assert_equals('box_type', node.box_type)
        self.assert_equals(Site, node.model)
        self.assert_equals(('slug', '"home"'), node.lookup)

