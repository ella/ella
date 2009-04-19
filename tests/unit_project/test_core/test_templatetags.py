# -*- coding: utf-8 -*-
from djangosanetesting import UnitTestCase

from django import template

from ella.core import register

class TestRenderTag(UnitTestCase):
    def test_raises_error_on_no_args(self):
        t = '{% render %}'
        self.assert_raises(template.TemplateSyntaxError, template.Template, t)

    def test_raises_error_on_more_args(self):
        t = '{% render 1 2 3 %}'
        self.assert_raises(template.TemplateSyntaxError, template.Template, t)

    def test_fail_silently_on_empty_var(self):
        t = template.Template('{% render var_name %}')
        self.assert_equals('', t.render(template.Context()))

    def test_renders_var(self):
        t = template.Template('{% render var %}')
        self.assert_equals('XXX', t.render(template.Context({'var': 'XXX'})))

    def test_renders_nested_var(self):
        t = template.Template('{% render var.subvar.subsubvar %}')
        var = {'subvar': {'subsubvar': 'XXX'}}
        self.assert_equals('XXX', t.render(template.Context({'var': var})))

    def test_renders_var_in_context(self):
        t = template.Template('{% render var %}')
        self.assert_equals('YYY', t.render(template.Context({'var': '{{ other_var }}', 'other_var' : 'YYY'})))

    def test_does_not_escape_output(self):
        t = template.Template('{% render var %}')
        self.assert_equals('<html> ""', t.render(template.Context({'var': '<html> ""'})))

