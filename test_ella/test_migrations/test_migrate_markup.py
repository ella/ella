from django.contrib.contenttypes.models import ContentType

from django.test import TestCase

from nose import tools

from ella.core.management.commands import migrate_markup
from ella.core.management.commands.migrate_markup import BOX_RE, update_field
from ella.core.models import Dependency

from test_ella.test_core import create_basic_categories, create_and_place_a_publishable

class TestUpdateField(TestCase):
    def setUp(self):
        super(TestUpdateField, self).setUp()
        migrate_markup.lookup = {}
        create_basic_categories(self)
        create_and_place_a_publishable(self)

    def tearDown(self):
        super(TestUpdateField, self).tearDown()
        migrate_markup.lookup = None

    def test_update_creates_no_dependency_if_no_box_in_text(self):
        tools.assert_equals(0, Dependency.objects.count())
        val = 'text'
        new_val, cnt = BOX_RE.subn(update_field(self.publishable, self.publishable.content_type), val)
        tools.assert_equals(val, new_val)
        tools.assert_equals(0, cnt)
        tools.assert_equals(0, Dependency.objects.count())


    def test_update_creates_a_dependency_for_box_in_text(self):
        tools.assert_equals(0, Dependency.objects.count())
        val = 'text {%% box name for core.category with pk %s %%}{%% endbox %%}' % self.category.pk
        new_val, cnt = BOX_RE.subn(update_field(self.publishable, self.publishable.content_type), val)
        tools.assert_equals(val, new_val)
        tools.assert_equals(1, cnt)
        tools.assert_equals(1, Dependency.objects.count())
        dep = Dependency.objects.all()[0]
        tools.assert_equals(self.publishable, dep.dependent)
        tools.assert_equals(self.category, dep.target)


    def test_update_updates_pk_and_creates_a_dependency_for_box_in_text(self):
        ct = ContentType.objects.get_for_model(self.category)
        migrate_markup.lookup[(ct.pk, self.category.pk)] = 123
        tools.assert_equals(0, Dependency.objects.count())

        base = 'text {%% box name for core.category with pk %s %%}{%% endbox %%}'
        val = base % self.category.pk
        new_val, cnt = BOX_RE.subn(update_field(self.publishable, self.publishable.content_type), val)

        tools.assert_equals(1, cnt)
        tools.assert_equals(base % 123, new_val)
        tools.assert_equals(1, Dependency.objects.count())
        dep = Dependency.objects.all()[0]
        tools.assert_equals(self.publishable, dep.dependent)
        tools.assert_equals(123, dep.target_id)


