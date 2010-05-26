# -*- coding: utf-8 -*-
from djangosanetesting import UnitTestCase, DatabaseTestCase

from django import template
from django.template import TemplateSyntaxError
from django.contrib.sites.models import Site

from ella.core.templatetags.core import listing_parse, ListingNode, _parse_box, BoxNode, EmptyNode
from ella.core.templatetags.hits import top_visited_parser
from ella.core.models import Listing, Category
from ella.core import register

from unit_project.test_core import create_basic_categories, create_and_place_a_publishable, \
        create_and_place_more_publishables, list_all_placements_in_category_by_hour, \
        create_and_place_two_publishables_and_listings
from unit_project import template_loader

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

class TestBoxTag(UnitTestCase):

    def tearDown(self):
        super(TestBoxTag, self).tearDown()
        template_loader.templates = {}

    def test_renders_correct_template(self):
        template_loader.templates['box/box.html'] = '{{ object }}'
        t = template.Template('{% box name for sites.site with pk 1 %}{% endbox %}')
        self.assert_equals('example.com', t.render(template.Context()))

    def test_params_are_parsed(self):
        template_loader.templates['box/box.html'] = '{% for k,v in box.params.items %}{{k}}:{{v}}|{% endfor %}'
        t = template.Template('''{% box name for sites.site with pk 1 %}
                level: 2
                some_other_param: xxx
            {% endbox %}''')
        self.assert_equals('some_other_param:xxx|level:2|', t.render(template.Context()))

    def test_box_wirks_with_variable_instead_of_lookup(self):
        site = Site.objects.get(pk=1)
        template_loader.templates['box/box.html'] = '{{ object }}'
        t = template.Template('{% box name for var %}{% endbox %}')
        self.assert_equals('example.com', t.render(template.Context({'var': site})))

    def test_box_for_empty_object_renders_empty(self):
        template_loader.templates['box/box.html'] = 'XXX'
        t = template.Template('{% box name for var %}{% endbox %}')
        self.assert_equals('', t.render(template.Context({'var': None})))

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

    def test_parse_raises_on_too_many_arguments(self):
        self.assert_raises(TemplateSyntaxError, _parse_box, [], ['box', 'box_type', 'for', 'core.category', 'with', 'pk', '1', '2', 'extra'])

    def test_parse_raises_on_too_few_arguments(self):
        self.assert_raises(TemplateSyntaxError, _parse_box, [], ['box', 'box_type', 'for'])

    def test_parse_raises_on_incorrect_arguments(self):
        self.assert_raises(TemplateSyntaxError, _parse_box, [], ['box', 'box_type', 'not a for', 'core.category', 'with', 'pk', '1'])

    def test_parse_return_empty_node_on_incorrect_model(self):
        node = _parse_box([], ['box', 'box_type', 'for', 'not_app.not_model', 'with', 'pk', '1'])
        self.assert_true(isinstance(node, EmptyNode))

class TestTopVisitedTagParser(UnitTestCase):
    '''
    {% top_visited <count> [days <days>] [app.model [app.model[...]]] as <result> %}
    '''

    def test_minimal_args(self):
        count, var_name, days, mods = top_visited_parser(['top_visited', '1', 'as', 'var'])
        self.assert_equals(1, count)
        self.assert_equals('var', var_name)
        self.assert_equals(None, days)
        self.assert_equals([], mods)

    def test_days(self):
        count, var_name, days, mods = top_visited_parser(['top_visited', '1', 'days', '7', 'as', 'var'])
        self.assert_equals(7, days)

    def test_one_model(self):
        from ella.articles.models import Article
        count, var_name, days, mods = top_visited_parser(['top_visited', '1', 'articles.article', 'as', 'var'])
        self.assert_equals([Article], mods)

    def test_more_models(self):
        from ella.articles.models import Article
        from ella.galleries.models import Gallery
        count, var_name, days, mods = top_visited_parser(['top_visited', '1', 'articles.article', 'galleries.gallery', 'as', 'var'])
        self.assert_equals([Article, Gallery], mods)

    def test_few_params(self):
        self.assert_raises(template.TemplateSyntaxError, top_visited_parser, ['top_visited', 'as', 'var'])

    def test_raises_error_count_not_int(self):
        self.assert_raises(template.TemplateSyntaxError, top_visited_parser, ['top_visited', 'I0', 'as', 'var'])

    def test_raises_error_days_not_int(self):
        self.assert_raises(template.TemplateSyntaxError, top_visited_parser, ['top_visited', '1', 'days', 'I0', 'as', 'var'])

    def test_raises_error_days_less_then_1(self):
        self.assert_raises(template.TemplateSyntaxError, top_visited_parser, ['top_visited', '1', 'days', '0', 'as', 'var'])

    def test_raises_error_on_no_as(self):
        self.assert_raises(template.TemplateSyntaxError, top_visited_parser, ['top_visited', '1', 'articles.article', 'var'])

    def test_raises_error_unknown_model(self):
        self.assert_raises(template.TemplateSyntaxError, top_visited_parser, ['top_visited', '1', 'articles.articl', 'as', 'var'])

class TestTopVisitedTag(DatabaseTestCase):
    def setUp(self):
        super(TestTopVisitedTag, self).setUp()
        create_basic_categories(self)
        create_and_place_two_publishables_and_listings(self)

    def test_get_all_top_visited(self):
        t = template.Template('{% load hits %}{% top_visited 5 as var %}{% for h in var %}{{ h.placement.publishable.id }}{% if not forloop.last %}:{% endif %}{% endfor %}')
        expected = ':'.join( [str(hitcount.placement.publishable.id) for hitcount in self.hitcounts_all] )
        self.assert_equals( expected, t.render(template.Context()) )

    def test_get_top_visited_count_limited(self):
        t = template.Template('{% load hits %}{% top_visited 1 as var %}{% for h in var %}{{ h.placement.publishable.id }}{% if not forloop.last %}:{% endif %}{% endfor %}')
        expected = str(self.hitcount_top.placement.publishable.id)
        self.assert_equals( expected, t.render(template.Context()) )

    def test_get_top_visited_age_limited(self):
        t = template.Template('{% load hits %}{% top_visited 5 days 8 as var %}{% for h in var %}{{ h.placement.publishable.id }}{% if not forloop.last %}:{% endif %}{% endfor %}')
        expected = ':'.join( [str(hitcount.placement.publishable.id) for hitcount in self.hitcounts_age_limited] )
        self.assert_equals( expected, t.render(template.Context()) )

    def test_get_top_visited_model_limited(self):
        t = template.Template('{% load hits %}{% top_visited 5 galleries.gallery as var %}{% for h in var %}{{ h.placement.publishable.id }}{% if not forloop.last %}:{% endif %}{% endfor %}')
        expected = ':'.join( [str(hitcount.placement.publishable.id) for hitcount in self.hitcounts_galleries] )
        self.assert_equals( expected, t.render(template.Context()) )
