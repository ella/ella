# -*- coding: utf-8 -*-
from django.forms import ValidationError
from django.db.models import signals

from djangosanetesting.cases import DatabaseTestCase

from ella.newman import fields
from ella.newman.licenses.models import License
from ella.core.models import Dependency

from unit_project.test_core import create_basic_categories, create_and_place_a_publishable

DROP_SIGNALS = [signals.pre_save, signals.post_save]
class RichTextFieldTestCase(DatabaseTestCase):
    def setUp(self):
        super(RichTextFieldTestCase, self).setUp()

        self.old_signal_receivers = []
        for s in DROP_SIGNALS:
            self.old_signal_receivers.append(s.receivers)
            s.receivers = []

        create_basic_categories(self)
        create_and_place_a_publishable(self)

        self.field = fields.NewmanRichTextField(
            instance=self.publishable,
            model=self.publishable.__class__,
            field_name = "description",
        )

    def tearDown(self):
        for s, rec in zip(DROP_SIGNALS, self.old_signal_receivers):
            s.receivers = rec


class TestRichTextFieldValidation(RichTextFieldTestCase):
    def tearDown(self):
        for s, rec in zip(DROP_SIGNALS, self.old_signal_receivers):
            s.receivers = rec

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

    def test_two_dependencies_in_two_fields_get_picked_up(self):
        field2 = fields.NewmanRichTextField(
            instance=self.publishable,
            model=self.publishable.__class__,
            field_name = "title",
        )

        text2 = 'some-text {%% box inline for core.category with pk %s %%}{%% endbox %%}' % self.category_nested.pk
        self.publishable.title = field2.clean(text2)

        text = 'some-text {%% box inline for core.category with pk %s %%}{%% endbox %%}' % self.category.pk
        self.publishable.description = self.field.clean(text)

        self.publishable.save()

        self.assert_equals(2, Dependency.objects.all().count())
        self.assert_equals(sorted([self.category.pk, self.category_nested.pk]), [dep.target_id for dep in Dependency.objects.order_by('target_id')])

    def test_object_still_used_in_one_field_doesnt_affect_dependencies(self):
        dep = Dependency()
        dep.target = self.category
        dep.dependent = self.publishable
        dep.save()

        text = 'some-text {%% box inline for core.category with pk %s %%}{%% endbox %%}' % self.category.pk

        field2 = fields.NewmanRichTextField(
            instance=self.publishable,
            model=self.publishable.__class__,
            field_name = "title",
        )

        self.publishable.title = field2.clean('no box here')
        self.publishable.description = self.field.clean(text)
        self.publishable.save()

        self.assert_equals(1, Dependency.objects.all().count())
        dep = Dependency.objects.all()[0]
        self.assert_equals(self.category, dep.target)
        self.assert_equals(self.publishable, dep.dependent)


class TestRichTextFieldLicenseHandling(RichTextFieldTestCase):

    def test_use_of_unlicensed_object_doesnt_do_anything(self):
        text = 'some-text {%% box inline for core.category with pk %s %%}{%% endbox %%}' % self.category.pk
        self.publishable.description = self.field.clean(text)
        self.publishable.save()

        self.assert_equals(0, License.objects.count())

    def test_use_of_licensed_object_raises_the_applications_counter(self):
        l = License(max_applications=2)
        l.target = self.category
        l.save()

        text = 'some-text {%% box inline for core.category with pk %s %%}{%% endbox %%}' % self.category.pk
        self.publishable.description = self.field.clean(text)
        self.publishable.save()
        self.assert_equals(1, License.objects.get(pk=l.pk).applications)

    def test_still_using_licensed_object_doesnt_change_its_applications(self):
        l = License(max_applications=2, applications=2)
        l.target = self.category
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
        l = License(max_applications=2, applications=2)
        l.target = self.category
        l.save()

        dep = Dependency()
        dep.target = self.category
        dep.dependent = self.publishable
        dep.save()

        text = 'some-text, no box'
        self.publishable.description = self.field.clean(text)
        self.publishable.save()

        self.assert_equals(1, License.objects.get(pk=l.pk).applications)

    def test_two_uses_in_two_fields_on_one_object_count_as_one(self):
        l = License(max_applications=2, applications=1)
        l.target = self.category
        l.save()

        text = 'some-text {%% box inline for core.category with pk %s %%}{%% endbox %%}' % self.category.pk
        self.publishable.description = self.field.clean(text)

        field2 = fields.NewmanRichTextField(
            instance=self.publishable,
            model=self.publishable.__class__,
            field_name = "title",
        )
        self.publishable.title = field2.clean(text)
        self.publishable.save()

        self.assert_equals(2, License.objects.get(pk=l.pk).applications)


    def test_object_still_used_in_one_field_doesnt_affect_applications(self):
        l = License(max_applications=2, applications=1)
        l.target = self.category
        l.save()

        dep = Dependency()
        dep.target = self.category
        dep.dependent = self.publishable
        dep.save()

        text = 'some-text {%% box inline for core.category with pk %s %%}{%% endbox %%}' % self.category.pk
        self.publishable.description = self.field.clean(text)

        field2 = fields.NewmanRichTextField(
            instance=self.publishable,
            model=self.publishable.__class__,
            field_name = "title",
        )
        self.publishable.title = field2.clean('no box here')
        self.publishable.save()

        self.assert_equals(1, License.objects.get(pk=l.pk).applications)


