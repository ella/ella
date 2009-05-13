# -*- coding: utf-8 -*-
from django.forms import ValidationError
 
from djangosanetesting.cases import DatabaseTestCase

from ella.newman import fields
from ella.newman.licenses.models import License
from ella.core.models import Dependency

from unit_project.test_core import create_basic_categories, create_and_place_a_publishable

class RichTextFieldTestCase(DatabaseTestCase):
    def setUp(self):
        super(RichTextFieldTestCase, self).setUp()
        create_basic_categories(self)
        create_and_place_a_publishable(self)

        self.field = fields.NewmanRichTextField(
            instance=self.publishable,
            model=self.publishable.__class__,
            field_name = "description",
        )


class TestRichTextFieldValidation(RichTextFieldTestCase):

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

class TestRichTextFieldDependencyHandling(RichTextFieldTestCase):

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

class TestRichTextFieldLicenseHandling(RichTextFieldTestCase):

    def test_use_of_unlicensed_object_doesnt_do_anything(self):
        text = 'some-text {%% box inline for core.category with pk %s %%}{%% endbox %%}' % self.category.pk
        self.publishable.description = self.field.clean(text)
        self.publishable.save()

        self.assert_equals(0, License.objects.count())

    def test_use_of_licensed_object_raises_the_applications_counter(self):
        l = License()
        l.target = self.category
        l.max_applications = 2
        l.save()

        text = 'some-text {%% box inline for core.category with pk %s %%}{%% endbox %%}' % self.category.pk
        self.publishable.description = self.field.clean(text)
        self.publishable.save()
        self.assert_equals(1, License.objects.get(pk=l.pk).applications)

    def test_still_using_licensed_object_doesnt_change_its_applications(self):
        l = License()
        l.target = self.category
        l.max_applications = 2
        l.applications = 2
        l.save()

        dep = Dependency()
        dep.target = self.category
        dep.dependent = self.publishable
        dep.save()

        text = 'some-text {%% box inline for core.category with pk %s %%}{%% endbox %%}' % self.category.pk
        self.publishable.description = self.field.clean(text)
        self.publishable.save()

        self.assert_equals(2, License.objects.get(pk=l.pk).applications)

    def test_no_longer_using_licensed_object_lowers_its_applications(self):
        l = License()
        l.target = self.category
        l.max_applications = 2
        l.applications = 2
        l.save()

        dep = Dependency()
        dep.target = self.category
        dep.dependent = self.publishable
        dep.save()

        text = 'some-text, no box'
        self.publishable.description = self.field.clean(text)
        self.publishable.save()

        self.assert_equals(1, License.objects.get(pk=l.pk).applications)





