# -*- coding: utf-8 -*-
from djangosanetesting.cases import DatabaseTestCase

from ella.core.models import Category
from ella.newman.licenses.models import License

from unit_project.test_core import create_basic_categories

class TestLicenseRestrictions(DatabaseTestCase):
    def setUp(self):
        super(TestLicenseRestrictions, self).setUp()
        create_basic_categories(self)

    def test_no_licenses_means_no_restrictions(self):
        self.assert_equals([], License.objects.unapplicable_for_model(Category))

    def test_license_no_uses_still_doesnt_limit(self):
        l = License()
        l.target = self.category
        l.max_applications = 2
        l.save()
        self.assert_equals([], License.objects.unapplicable_for_model(Category))

    def test_license_with_allowed_number_of_uses_still_doesnt_limit(self):
        l = License()
        l.target = self.category
        l.max_applications = 2
        l.applications = 1
        l.save()

        qset = Category.objects.order_by('pk')
        self.assert_equals([], License.objects.unapplicable_for_model(Category))
        self.assert_equals(list(qset), list(License.objects.filter_queryset(qset)))

    def test_license_with_max_number_of_uses_does_limit(self):
        l = License()
        l.target = self.category
        l.max_applications = 2
        l.applications = 2
        l.save()
        self.assert_equals([self.category.pk], License.objects.unapplicable_for_model(Category))

        qset = Category.objects.order_by('pk')
        self.assert_equals(list(qset.exclude(pk=self.category.pk)), list(License.objects.filter_queryset(qset)))

    def test_license_with_over_max_number_of_uses_does_limit(self):
        l = License()
        l.target = self.category
        l.max_applications = 2
        l.applications = 20
        l.save()
        self.assert_equals([self.category.pk], License.objects.unapplicable_for_model(Category))

        qset = Category.objects.order_by('pk')
        self.assert_equals(list(qset.exclude(pk=self.category.pk)), list(License.objects.filter_queryset(qset)))
