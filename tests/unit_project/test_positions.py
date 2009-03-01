# -*- coding: utf-8 -*-
from djangosanetesting import DatabaseTestCase

from unit_project.test_core import create_basic_categories

from ella.positions.models import Position

class TestPosition(DatabaseTestCase):

    def setUp(self):
        super(TestPosition, self).setUp()
        create_basic_categories(self)

    def test_get_active_position(self):
        p = Position.objects.create(category=self.category, name='position-name', text='some text')
        self.assert_equals(p, Position.objects.get_active_position(self.category, 'position-name'))

    def test_get_active_position_nofallback(self):
        p = Position.objects.create(category=self.category, name='position-name', text='some text')
        self.assert_equals(p, Position.objects.get_active_position(self.category, 'position-name', nofallback=True))

    def test_get_active_position_inherit(self):
        p = Position.objects.create(category=self.category, name='position-name', text='some text')
        self.assert_equals(p, Position.objects.get_active_position(self.category_nested, 'position-name'))

    def test_get_active_position_inherit_nofallback(self):
        p = Position.objects.create(category=self.category, name='position-name', text='some text')
        self.assert_raises(Position.DoesNotExist, Position.objects.get_active_position, self.category_nested, 'position-name', nofallback=True)

    def test_get_active_position_empty(self):
        self.assert_raises(Position.DoesNotExist, Position.objects.get_active_position, self.category, 'position-name')

