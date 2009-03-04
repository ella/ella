# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
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

    def test_active_till_past(self):
        p = Position.objects.create(category=self.category, name='position-name', text='some text', active_till=datetime.now()-timedelta(days=1))
        self.assert_raises(Position.DoesNotExist, Position.objects.get_active_position, self.category, 'position-name')

    def test_active_from_future(self):
        p = Position.objects.create(category=self.category, name='position-name', text='some text', active_from=datetime.now()+timedelta(days=1))
        self.assert_raises(Position.DoesNotExist, Position.objects.get_active_position, self.category, 'position-name')

    def test_active_till_future(self):
        p = Position.objects.create(category=self.category, name='position-name', text='some text', active_till=datetime.now()+timedelta(days=1))
        self.assert_equals(p, Position.objects.get_active_position(self.category_nested, 'position-name'))

    def test_active_from_past(self):
        p = Position.objects.create(category=self.category, name='position-name', text='some text', active_from=datetime.now()-timedelta(days=1))
        self.assert_equals(p, Position.objects.get_active_position(self.category_nested, 'position-name'))

    def test_active_from_till_match(self):
        p = Position.objects.create(category=self.category, name='position-name', text='some text',
                active_from=datetime.now()-timedelta(days=1),
                active_till=datetime.now()+timedelta(days=1),
            )
        self.assert_equals(p, Position.objects.get_active_position(self.category_nested, 'position-name'))

    def test_active_from_till_no_match(self):
        p = Position.objects.create(category=self.category, name='position-name', text='some text',
                active_from=datetime.now()-timedelta(days=3),
                active_till=datetime.now()-timedelta(days=1),
            )
        self.assert_raises(Position.DoesNotExist, Position.objects.get_active_position, self.category, 'position-name')

    def test_more_positions_one_active(self):
        p1 = Position.objects.create(category=self.category, name='position-name', text='some text',
                active_from=datetime.now()-timedelta(days=1),
            )
        p2 = Position.objects.create(category=self.category, name='position-name', text='some text', active_till=datetime.now()-timedelta(days=1))
        self.assert_equals(p1, Position.objects.get_active_position(self.category_nested, 'position-name'))

    def test_not_disabled(self):
        p = Position.objects.create(category=self.category, name='position-name', text='some text', disabled=False)
        self.assert_equals(p, Position.objects.get_active_position(self.category, 'position-name'))

    def test_disabled(self):
        p = Position.objects.create(category=self.category, name='position-name', text='some text', disabled=True)
        self.assert_raises(Position.DoesNotExist, Position.objects.get_active_position, self.category, 'position-name')

