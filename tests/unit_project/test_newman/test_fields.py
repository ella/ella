# -*- coding: utf-8 -*-
from django.forms import ValidationError
 
from djangosanetesting.cases import DatabaseTestCase

from ella.newman import fields
from ella.core.models import Dependency

from unit_project.test_core import create_basic_categories, create_and_place_a_publishable

class TestNewmanRichTextField(DatabaseTestCase):
    def setUp(self):
        super(TestNewmanRichTextField, self).setUp()
        create_basic_categories(self)
        create_and_place_a_publishable(self)

        self.field = fields.NewmanRichTextField(
            instance=self.publishable,
            model=self.publishable.__class__,
            field_name = "description",
        )


    def test_field_doesnt_validate_invalid_template(self):
        self.assert_raises(ValidationError, self.field.clean, '{% not-a-tag %}')

    def test_field_doesnt_validate_tamplate_with_tags(self):
        self.assert_raises(ValidationError, self.field.clean, '{% if 1 %}XX {% endif %}')


    def test_field_doesnt_validate_template_with_boxes_with_variables(self):
        self.assert_raises(ValidationError, self.field.clean, '{% box name for var %}{% endbox %}')


    def test_field_doesnt_validate_boxes_for_missing_objects(self):
        self.assert_raises(ValidationError, self.field.clean, '{% box name for articles.article with pk 10000 %}{% endbox %}')

    def test_field_validates_pure_text(self):
        self.assert_equals(self.field.processor.convert('some-text'), self.field.clean('some-text'))

    def test_field_validates_text_and_correct_boxes(self):
        text = 'some-text {%% box inline for core.category with pk %s %%}{%% endbox %%}' % self.category.pk
        self.assert_equals(self.field.processor.convert(text), self.field.clean(text))

    def test_field_creates_dependencies_for_embedded_objects(self):
        text = 'some-text {%% box inline for core.category with pk %s %%}{%% endbox %%}' % self.category.pk
        self.publishable.description = self.field.clean(text)
        self.publishable.save()

        self.assert_equals(1, Dependency.objects.all().count())
        dep = Dependency.objects.all()[0]
        self.assert_equals(self.category, dep.target)
        self.assert_equals(self.publishable, dep.dependent)

    def test_field_drops_dependencies_on_update(self):
        dep = Dependency()
        dep.target = self.category
        dep.dependent = self.publishable
        dep.save()

        text = 'some-text no boxes'
        self.publishable.description = self.field.clean(text)
        self.publishable.save()

        self.assert_equals(0, Dependency.objects.all().count())
