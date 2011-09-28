# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from djangosanetesting import DatabaseTestCase

from django.template import Context, NodeList
from django.contrib.contenttypes.models import ContentType
from django.db.models import Max

from unit_project.test_core import create_basic_categories

from ella.positions.models import Position

class TestPosition(DatabaseTestCase):

    def setUp(self):
        super(TestPosition, self).setUp()
        create_basic_categories(self)

    def test_render_position_without_target_renders_txt(self):
        p = Position.objects.create(category=self.category, name='position-name', text='some text')
        self.assert_equals('some text', p.render(Context({}), NodeList(), ''))

    def test_render_position_with_invalid_target_returns_empty(self):
        target_ct = ContentType.objects.get_for_model(ContentType)
        invalid_id = ContentType.objects.aggregate(Max('id'))['id__max'] + 1

        p = Position.objects.create(category=self.category, name='position-name', text='some text', target_ct=target_ct, target_id=invalid_id)
        self.assert_equals('', p.render(Context({}), NodeList(), ''))

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

    def test_position_with_broken_definition_dont_raise_big_500(self):
        p = Position.objects.create(category=self.category, name='position-name', text='{% load nonexistent_tags %}', disabled=False)
        self.assert_equals('', p.render(Context({}), NodeList(), ''))

