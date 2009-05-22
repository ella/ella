# -*- coding: utf-8 -*-
from djangosanetesting import UnitTestCase, DatabaseTestCase

from django import template

from ella.core.templatetags.core import listing_parse, ListingNode
from ella.core.models import Listing
from ella.core import register

from unit_project.test_core import create_basic_categories, create_and_place_a_publishable, \
        create_and_place_more_publishables, list_all_placements_in_category_by_hour

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

class TestListingTag(DatabaseTestCase):
    def setUp(self):
        super(TestListingTag, self).setUp()
        create_basic_categories(self)
        create_and_place_a_publishable(self)
        create_and_place_more_publishables(self)
        list_all_placements_in_category_by_hour(self)

    def test_get_listing(self):
        t = template.Template('{% listing 10 for category as var %}{{ var|join:":" }}')
        expected = ':'.join([str(listing) for listing in self.listings if listing.category == self.category])
        self.assert_equals(expected, t.render(template.Context({'category': self.category})))

    def test_get_listing_with_immediate_children(self):
        t = template.Template('{% listing 10 for category with children as var %}{{ var|join:":" }}')
        expected = ':'.join([str(listing) for listing in self.listings if listing.category in (self.category, self.category_nested)])
        self.assert_equals(expected, t.render(template.Context({'category': self.category})))

    def test_get_listing_with_immediate_children_and_offset(self):
        t = template.Template('{% listing 10 from 2 for category with children as var %}{{ var|join:":" }}')
        expected = ':'.join([str(listing) for listing in self.listings if listing.category in (self.category, self.category_nested)][1:])
        self.assert_equals(expected, t.render(template.Context({'category': self.category})))

    def test_get_listing_with_immediate_children_offset_and_count(self):
        t = template.Template('{% listing 1 from 2 for category with children as var %}{{ var|join:":" }}')
        expected = [str(listing) for listing in self.listings if listing.category in (self.category, self.category_nested)][1]
        self.assert_equals(expected, t.render(template.Context({'category': self.category})))

class TestListingTagParser(UnitTestCase):
    '''
    {% listing <limit>[ from <offset>][of <app.model>[, <app.model>[, ...]]][ for <category> ] [with children|descendents] as <result> %}
    '''

    def test_minimal_args(self):
        var_name, parameters, parameters_to_resolve = listing_parse(['listing', '1', 'as', 'var'])
        self.assert_equals('var', var_name)
        self.assert_equals({'count': '1'}, parameters)
        self.assert_equals(['count'], parameters_to_resolve)

    def test_offset(self):
        var_name, parameters, parameters_to_resolve = listing_parse(['listing', '1', 'from', '10', 'as', 'var'])
        self.assert_true('offset' in parameters_to_resolve)
        self.assert_equals('10', parameters['offset'])

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

