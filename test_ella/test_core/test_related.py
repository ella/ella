# -*- coding: utf-8 -*-
from unittest import TestCase as UnitTestCase
from test_ella.cases import RedisTestCase as TestCase

from nose import tools

from ella.articles.models import Article
from ella.core.models import Related, Publishable
from ella.core.templatetags.related import parse_related_tag
from ella.photos.models import Photo

from test_ella.test_core import create_basic_categories, create_and_place_a_publishable, \
        create_and_place_more_publishables, list_all_publishables_in_category_by_hour

class GetRelatedTestCase(TestCase):
    def setUp(self):
        super(GetRelatedTestCase, self).setUp()
        create_basic_categories(self)
        create_and_place_a_publishable(self)
        create_and_place_more_publishables(self)

        Publishable.objects.all().update(category=self.publishable.category)

        list_all_publishables_in_category_by_hour(self, category=self.publishable.category)

class TestDefaultRelatedFinder(GetRelatedTestCase):
    def test_returns_unique_objects_or_shorter_list_if_not_available(self):
        expected = map(lambda x: x.pk, reversed(self.publishables))
        tools.assert_equals(
                expected,
                [p.pk for p in Related.objects.get_related_for_object(self.publishable, len(expected)*3)]
            )

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
        r = Related(publishable=self.publishable)
        r.related = self.publishables[0]
        r.save()

        tools.assert_equals(
                [self.publishables[0].pk, self.publishables[-1].pk],
                [p.pk for p in Related.objects.get_related_for_object(self.publishable, 2, mods=[self.publishable.__class__])]
            )

    def test_returns_manual_objects_first(self):
        r = Related(publishable=self.publishable)
        r.related = self.category
        r.save()

        tools.assert_equals(
                [self.category, self.publishables[-1]],
                Related.objects.get_related_for_object(self.publishable, 2)
            )

    def test_returns_only_manual_objects_when_direct_finder_specified(self):
        r = Related(publishable=self.publishable)
        r.related = self.publishables[0]
        r.save()

        tools.assert_equals(
                [self.publishables[0].pk],
                [p.pk for p in Related.objects.get_related_for_object(self.publishable, 2, finder='directly')]
            )

    def test_returns_unique_objects(self):
        r = Related(publishable=self.publishable)
        r.related = self.publishables[-2]
        r.save()

        tools.assert_equals(
                [self.publishables[-2].pk, self.publishables[-1].pk, self.publishables[-3].pk],
                [p.pk for p in Related.objects.get_related_for_object(self.publishable, 3)]
            )

    def test_returns_empty_if_no_object_of_given_model_is_available(self):
        r = Related(publishable=self.publishables[0])
        r.related = self.publishable
        r.save()
        tools.assert_equals([], Related.objects.get_related_for_object(self.publishable, 3, mods=[Related]))


class TestRelatedTagParser(UnitTestCase):
    '''
    {% related N [app_label.Model, ...] for object as var_name %}
    '''
    def setUp(self):
        super(TestRelatedTagParser, self).setUp()
        self.minimal_args = ['related', '10', 'for', 'obj_var', 'as', 'some_var']

    def test_minimal_args(self):
        obj_var, count, var_name, mods, finder = parse_related_tag(self.minimal_args)
        tools.assert_equals('obj_var', obj_var)
        tools.assert_equals(10, count)
        tools.assert_equals('some_var', var_name)
        tools.assert_equals([], mods)
        tools.assert_equals(None, finder)

    def test_limit_bu_model(self):
        self.minimal_args.insert(2, 'articles.article')
        obj_var, count, var_name, mods, finder = parse_related_tag(self.minimal_args)
        tools.assert_equals('obj_var', obj_var)
        tools.assert_equals(10, count)
        tools.assert_equals('some_var', var_name)
        tools.assert_equals([Article], mods)
        tools.assert_equals(None, finder)

    def test_limit_bu_more_models(self):
        self.minimal_args.insert(2, 'articles.article,photos.photo')
        obj_var, count, var_name, mods, finder = parse_related_tag(self.minimal_args)
        tools.assert_equals('obj_var', obj_var)
        tools.assert_equals(10, count)
        tools.assert_equals('some_var', var_name)
        tools.assert_equals([Article, Photo], mods)
        tools.assert_equals(None, finder)

    def test_limit_bu_more_models_with_space(self):
        self.minimal_args.insert(2, 'articles.article,')
        self.minimal_args.insert(3, 'photos.photo')
        obj_var, count, var_name, mods, finder = parse_related_tag(self.minimal_args)
        tools.assert_equals('obj_var', obj_var)
        tools.assert_equals(10, count)
        tools.assert_equals('some_var', var_name)
        tools.assert_equals([Article, Photo], mods)
        tools.assert_equals(None, finder)

    def test_limit_bu_more_models_with_spaces_around_comma(self):
        self.minimal_args.insert(2, 'articles.article')
        self.minimal_args.insert(3, ',')
        self.minimal_args.insert(4, 'photos.photo')
        obj_var, count, var_name, mods, finder = parse_related_tag(self.minimal_args)
        tools.assert_equals('obj_var', obj_var)
        tools.assert_equals(10, count)
        tools.assert_equals('some_var', var_name)
        tools.assert_equals([Article, Photo], mods)
        tools.assert_equals(None, finder)

    def test_finder_is_defined_before_model_specs(self):
        self.minimal_args.insert(2, 'directly')
        self.minimal_args.insert(3, 'articles.article')
        self.minimal_args.insert(4, ',')
        self.minimal_args.insert(5, 'photos.photo')
        obj_var, count, var_name, mods, finder = parse_related_tag(self.minimal_args)
        tools.assert_equals('obj_var', obj_var)
        tools.assert_equals(10, count)
        tools.assert_equals('some_var', var_name)
        tools.assert_equals([Article, Photo], mods)
        tools.assert_equals("directly", finder)

