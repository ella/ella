# -*- coding: utf-8 -*-
from unittest import TestCase as UnitTestCase
from django.test import TestCase

from nose import tools

from ella.core.templatetags.related import parse_related_tag, RelatedNode
from ella.core.models import Related, Publishable

from unit_project.test_core import create_basic_categories, create_and_place_a_publishable, \
        create_and_place_more_publishables, list_all_placements_in_category_by_hour

class GetRelatedTestCase(TestCase):
    def setUp(self):
        super(GetRelatedTestCase, self).setUp()
        create_basic_categories(self)
        create_and_place_a_publishable(self)
        create_and_place_more_publishables(self)

        Publishable.objects.all().update(category=self.publishable.category)

        list_all_placements_in_category_by_hour(self, category=self.publishable.category)

class TestGetRelated(GetRelatedTestCase):
    def test_returns_publishables_listed_in_same_cat_if_no_related(self):
        expected = map(lambda x: x.pk, reversed(self.publishables))
        tools.assert_equals(
                expected,
                [p.pk for p in Related.objects.get_related_for_object(self.publishable, len(expected))]
            )

    def test_returns_at_most_count_objects(self):
        tools.assert_equals(
                [self.publishables[-1].pk],
                [p.pk for p in Related.objects.get_related_for_object(self.publishable, 1)]
            )

    def test_returns_manual_objects_of_correct_model_type_first(self):
        r = Related(publishable=self.publishables[0])
        r.related = self.publishable
        r.save()

        tools.assert_equals(
                [self.publishables[0].pk, self.publishables[-1].pk],
                [p.pk for p in Related.objects.get_related_for_object(self.publishable, 2, mods=[self.publishable.__class__])]
            )

    def test_returns_manual_objects_first(self):
        r = Related(publishable=self.publishables[0])
        r.related = self.publishable
        r.save()

        tools.assert_equals(
                [self.publishables[0].pk, self.publishables[-1].pk],
                [p.pk for p in Related.objects.get_related_for_object(self.publishable, 2)]
            )

    def test_returns_unique_objects(self):
        r = Related(publishable=self.publishables[-2])
        r.related = self.publishable
        r.save()

        tools.assert_equals(
                [self.publishables[-2].pk, self.publishables[-1].pk, self.publishables[-3].pk],
                [p.pk for p in Related.objects.get_related_for_object(self.publishable, 3)]
            )

    def test_returns_empty_if_no_object_of_given_model_is_availible(self):
        r = Related(publishable=self.publishables[0])
        r.related = self.publishable
        r.save()
        tools.assert_equals([], Related.objects.get_related_for_object(self.publishable, 3, mods=[Related]))


class TestGetRelatedWithtagging(GetRelatedTestCase):
    def setUp(self):
        try:
            import tagging
        except ImportError, e:
            raise self.SkipTest()
        super(TestGetRelatedWithtagging, self).setUp()
        from tagging.models import Tag, TaggedItem
        self.Tag = Tag
        self.TaggedItem = TaggedItem

    def test_returns_object_with_similar_tags(self):
        self.Tag.objects.update_tags(self.only_publishable, 'tag1 tag2')
        p = Publishable.objects.get(pk=self.publishables[0].pk)
        self.Tag.objects.update_tags(p, 'tag1 tag2')

        tools.assert_equals([p], Related.objects.get_related_for_object(self.publishable, 1))

class TestRelatedTagParser(UnitTestCase):
    '''
    {% related N [app_label.Model, ...] for object as var_name %}
    '''
    def setUp(self):
        super(TestRelatedTagParser, self).setUp()
        self.minimal_args = ['related', '10', 'for', 'obj_var', 'as', 'some_var']

    def test_minimal_args(self):
        obj_var, count, var_name, mods = parse_related_tag(self.minimal_args)
        tools.assert_equals('obj_var', obj_var)
        tools.assert_equals(10, count)
        tools.assert_equals('some_var', var_name)
        tools.assert_equals([], mods)

    def test_limit_bu_model(self):
        from ella.articles.models import Article, ArticleContents
        self.minimal_args.insert(2, 'articles.article')
        obj_var, count, var_name, mods = parse_related_tag(self.minimal_args)
        tools.assert_equals('obj_var', obj_var)
        tools.assert_equals(10, count)
        tools.assert_equals('some_var', var_name)
        tools.assert_equals([Article], mods)

    def test_limit_bu_more_models(self):
        from ella.articles.models import Article, ArticleContents
        self.minimal_args.insert(2, 'articles.article,articles.articlecontents')
        obj_var, count, var_name, mods = parse_related_tag(self.minimal_args)
        tools.assert_equals('obj_var', obj_var)
        tools.assert_equals(10, count)
        tools.assert_equals('some_var', var_name)
        tools.assert_equals([Article, ArticleContents], mods)

    def test_limit_bu_more_models_with_space(self):
        from ella.articles.models import Article, ArticleContents
        self.minimal_args.insert(2, 'articles.article,')
        self.minimal_args.insert(3, 'articles.articlecontents')
        obj_var, count, var_name, mods = parse_related_tag(self.minimal_args)
        tools.assert_equals('obj_var', obj_var)
        tools.assert_equals(10, count)
        tools.assert_equals('some_var', var_name)
        tools.assert_equals([Article, ArticleContents], mods)

    def test_limit_bu_more_models_with_spaces_around_comma(self):
        from ella.articles.models import Article, ArticleContents
        self.minimal_args.insert(2, 'articles.article')
        self.minimal_args.insert(3, ',')
        self.minimal_args.insert(4, 'articles.articlecontents')
        obj_var, count, var_name, mods = parse_related_tag(self.minimal_args)
        tools.assert_equals('obj_var', obj_var)
        tools.assert_equals(10, count)
        tools.assert_equals('some_var', var_name)
        tools.assert_equals([Article, ArticleContents], mods)

