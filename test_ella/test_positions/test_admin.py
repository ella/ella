# -*- coding: utf-8 -*-
from test_ella.cases import RedisTestCase as TestCase

from nose import tools

from django.contrib.contenttypes.models import ContentType
from django.contrib import admin

from test_ella.test_core import create_basic_categories, create_and_place_a_publishable

from ella.core.models import Author
from ella.positions.admin import PositionOptions
from ella.positions.models import Position


class TestPositionAdmin(TestCase):

    def setUp(self):
        super(TestPositionAdmin, self).setUp()
        create_basic_categories(self)
        create_and_place_a_publishable(self)
        self.author = Author.objects.create(slug='some-author')
        self.position_admin = PositionOptions(model=Position, admin_site=admin.site)

    def test_result_of_show_title_for_obj_with_title_attr(self):
        p = Position(category=self.category, name='position-name', target_ct=self.publishable.content_type, target_id=self.publishable.pk)
        tools.assert_equals(u'%s [%s]' % (self.publishable.title, self.publishable.content_type.name), self.position_admin.show_title(p))

    def test_result_of_show_title_for_obj_without_title_attr(self):
        ct = ContentType.objects.get_for_model(Author)
        p = Position(category=self.category, name='position-name', target_ct=ct, target_id=self.author.pk)
        tools.assert_equals(u'%s [%s]' % (self.author, ct.name), self.position_admin.show_title(p))

    def test_result_of_show_title_for_position_without_trget(self):
        p = Position(category=self.category, name='position-name')
        tools.assert_true(self.position_admin.show_title(p).startswith('--'))
