# -*- coding: utf-8 -*-
from djangosanetesting import UnitTestCase

from django import template

from ella.core.templatetags.core import listing_parse, ListingNode
from ella.core.models import Listing
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

class TestListingTagParser(UnitTestCase):
    '''
    {% listing <limit>[ from <offset>][of <app.model>[, <app.model>[, ...]]][ for <category> ] [with children|descendents] as <result> %}
    '''

    def test_minimal_args(self):
        var_name, parameters, parameters_to_resolve = listing_parse(['listing', '1', 'as', 'var'])
        self.assert_equals('var', var_name)
        self.assert_equals({'count': '1'}, parameters)
        self.assert_equals(['count'], parameters_to_resolve)

    def test_limit_by_model(self):
        from ella.articles.models import Article, ArticleContents
        var_name, parameters, parameters_to_resolve = listing_parse(['listing', '1', 'of', 'articles.article', 'as', 'var'])
        self.assert_equals('var', var_name)
        self.assert_equals('1', parameters['count'])
        self.assert_equals([Article], parameters['mods'])

    def test_limit_bu_more_models(self):
        from ella.articles.models import Article, ArticleContents
        var_name, parameters, parameters_to_resolve = listing_parse(['listing', '1', 'of', 'articles.article,articles.articlecontents', 'as', 'var'])
        self.assert_equals([Article, ArticleContents], parameters['mods'])

    def test_limit_bu_more_models_space(self):
        from ella.articles.models import Article, ArticleContents
        var_name, parameters, parameters_to_resolve = listing_parse(['listing', '1', 'of', 'articles.article,', 'articles.articlecontents', 'as', 'var'])
        self.assert_equals([Article, ArticleContents], parameters['mods'])

    def test_limit_bu_more_models_space_around_comma(self):
        from ella.articles.models import Article, ArticleContents
        var_name, parameters, parameters_to_resolve = listing_parse(['listing', '1', 'of', 'articles.article', ',', 'articles.articlecontents', 'as', 'var'])
        self.assert_equals([Article, ArticleContents], parameters['mods'])

    def test_limit_by_category(self):
        var_name, parameters, parameters_to_resolve = listing_parse(['listing', '1', 'for', 'category', 'as', 'var'])
        self.assert_equals('category', parameters['category'])
        self.assert_equals(['count', 'category'], parameters_to_resolve)

    def test_limit_by_category_with_descendents(self):
        var_name, parameters, parameters_to_resolve = listing_parse(['listing', '1', 'for', 'category', 'with', 'descendents', 'as', 'var'])
        self.assert_equals('category', parameters['category'])
        self.assert_equals(['count', 'category'], parameters_to_resolve)
        self.assert_equals(Listing.objects.ALL, parameters['children'])

    def test_limit_by_category_with_children(self):
        var_name, parameters, parameters_to_resolve = listing_parse(['listing', '1', 'for', 'category', 'with', 'children', 'as', 'var'])
        self.assert_equals('category', parameters['category'])
        self.assert_equals(['count', 'category'], parameters_to_resolve)
        self.assert_equals(Listing.objects.IMMEDIATE, parameters['children'])

