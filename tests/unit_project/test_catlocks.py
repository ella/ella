# -*- coding: utf-8 -*-
import sys
import django

from djangosanetesting import DatabaseTestCase

from ella.catlocks.models import CategoryLock
from ella.catlocks.forms import CATEGORY_LOCK_FORM
from ella.catlocks.middleware import CATEGORY_LOCK_ERR_CAT

from unit_project.test_core import create_basic_categories
from unit_project import template_loader

class TestCatlock(DatabaseTestCase):
    def setUp(self):
        create_basic_categories(self)
        self.cl1 = CategoryLock.objects.create(category=self.category_nested, password='secret')
        template_loader.templates = {'page/category.html': ''}
        super(TestCatlock, self).setUp()

    def tearDown(self):
        super(TestCatlock, self).tearDown()
        template_loader.templates = {}

    def test_not_locked_category_is_uneffected(self):
        resp = self.client.get(self.category.get_absolute_url())
        self.assert_equals(200, resp.status_code)

    def test_locked_category_returns_302(self):
        resp = self.client.get(self.category_nested.get_absolute_url())
        self.assert_equals(302, resp.status_code)

    def test_locked_category_subpage_returns_302(self):
        resp = self.client.get(self.category_nested_second.get_absolute_url())
        self.assert_equals(302, resp.status_code)

    def test_sending_correct_password_unlocks_category(self):
        data = {CATEGORY_LOCK_FORM: self.category_nested.pk, 'password': 'secret'}

        resp = self.client.post(self.category_nested.get_absolute_url(), data)
        self.assert_equals(302, resp.status_code)

        # http://code.djangoproject.com/changeset/11821
        if django.VERSION < (1, 2) and sys.version_info > (2, 6, 4):
            raise self.SkipTest()

        resp = self.client.get(self.category_nested.get_absolute_url())
        self.assert_equals(200, resp.status_code)

    def test_sending_incorrect_password_doesnt_unlock_category(self):
        data = {CATEGORY_LOCK_FORM: self.category_nested.pk, 'password': 'not-a-secret'}

        resp = self.client.post(self.category_nested.get_absolute_url(), data)
        self.assert_equals(302, resp.status_code)

        resp = self.client.get(self.category_nested.get_absolute_url())

    def test_sending_incorrect_password_sets_error_flag(self):
        data = {CATEGORY_LOCK_FORM: self.category_nested.pk, 'password': 'not-a-secret'}

        resp = self.client.post(self.category_nested.get_absolute_url(), data)
        self.assert_equals(302, resp.status_code)
        self.assert_true(CATEGORY_LOCK_ERR_CAT in self.client.session)
        self.assert_equals(self.category_nested.pk, self.client.session[CATEGORY_LOCK_ERR_CAT].pk)

