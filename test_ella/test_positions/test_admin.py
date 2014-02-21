# -*- coding: utf-8 -*-
from unittest import TestCase

from nose import tools

from django.contrib import admin

from ella.core.models import Author
from ella.articles.models import Article
from ella.positions.admin import PositionOptions
from ella.positions.models import Position


class TestPositionAdmin(TestCase):

    def setUp(self):
        super(TestPositionAdmin, self).setUp()
        self.author = Author(slug='some-author')
        self.position_admin = PositionOptions(model=Position, admin_site=admin.site)

    def test_result_of_show_title_for_obj_with_title_attr(self):
        art = Article(title='Hello')
        p = Position()
        p.target = art
        tools.assert_equals(u'Hello [Article]', self.position_admin.show_title(p))

    def test_result_of_show_title_for_obj_without_title_attr(self):
        aut = Author(name='Hi!')
        p = Position()
        p.target = aut
        tools.assert_equals(u'Hi! [Author]', self.position_admin.show_title(p))

    def test_result_of_show_title_for_position_without_trget(self):
        p = Position()
        tools.assert_true(self.position_admin.show_title(p).startswith('--'))
