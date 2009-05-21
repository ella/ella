# -*- coding: utf-8 -*-
from djangosanetesting import UnitTestCase

from ella.core.templatetags.related import parse_related_tag, RelatedNode

class TestRelatedTagParser(UnitTestCase):
    '''
    {% related N [app_label.Model, ...] for object as var_name %}
    '''
    def setUp(self):
        super(TestRelatedTagParser, self).setUp()
        self.minimal_args = ['related', '10', 'for', 'obj_var', 'as', 'some_var']

    def test_minimal_args(self):
        obj_var, count, var_name, mods = parse_related_tag(self.minimal_args)
        self.assert_equals('obj_var', obj_var)
        self.assert_equals(10, count)
        self.assert_equals('some_var', var_name)
        self.assert_equals([], mods)

    def test_limit_bu_model(self):
        from ella.articles.models import Article, ArticleContents
        self.minimal_args.insert(2, 'articles.article')
        obj_var, count, var_name, mods = parse_related_tag(self.minimal_args)
        self.assert_equals('obj_var', obj_var)
        self.assert_equals(10, count)
        self.assert_equals('some_var', var_name)
        self.assert_equals([Article], mods)

    def test_limit_bu_more_models(self):
        from ella.articles.models import Article, ArticleContents
        self.minimal_args.insert(2, 'articles.article,articles.articlecontents')
        obj_var, count, var_name, mods = parse_related_tag(self.minimal_args)
        self.assert_equals('obj_var', obj_var)
        self.assert_equals(10, count)
        self.assert_equals('some_var', var_name)
        self.assert_equals([Article, ArticleContents], mods)

    def test_limit_bu_more_models_with_space(self):
        from ella.articles.models import Article, ArticleContents
        self.minimal_args.insert(2, 'articles.article,')
        self.minimal_args.insert(3, 'articles.articlecontents')
        obj_var, count, var_name, mods = parse_related_tag(self.minimal_args)
        self.assert_equals('obj_var', obj_var)
        self.assert_equals(10, count)
        self.assert_equals('some_var', var_name)
        self.assert_equals([Article, ArticleContents], mods)

    def test_limit_bu_more_models_with_spaces_around_comma(self):
        from ella.articles.models import Article, ArticleContents
        self.minimal_args.insert(2, 'articles.article')
        self.minimal_args.insert(3, ',')
        self.minimal_args.insert(4, 'articles.articlecontents')
        obj_var, count, var_name, mods = parse_related_tag(self.minimal_args)
        self.assert_equals('obj_var', obj_var)
        self.assert_equals(10, count)
        self.assert_equals('some_var', var_name)
        self.assert_equals([Article, ArticleContents], mods)

