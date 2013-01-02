# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from test_ella.cases import RedisTestCase as TestCase

from nose import tools

from django.template import Context, NodeList
from django.contrib.contenttypes.models import ContentType
from django.db.models import Max
from django.core.exceptions import ValidationError

from test_ella.test_core import create_basic_categories

from ella.positions.models import Position
from ella.utils.timezone import now, utc_localize

class TestPosition(TestCase):

    def setUp(self):
        super(TestPosition, self).setUp()
        create_basic_categories(self)

    def test_validation_fails_for_globaly_active_positions(self):
        Position.objects.create(category=self.category, name='position-name', text='some text')
        p = Position(category=self.category, name='position-name', text='other text')
        tools.assert_raises(ValidationError, p.full_clean)

    def test_validation_fails_for_overlapping_positions(self):
        Position.objects.create(category=self.category, name='position-name', text='some text', active_till=utc_localize(datetime(2010, 10, 10)))
        p = Position(category=self.category, name='position-name', text='other text')
        tools.assert_raises(ValidationError, p.full_clean)

    def test_validation_fails_for_overlapping_positions2(self):
        Position.objects.create(category=self.category, name='position-name', text='some text', active_till=utc_localize(datetime(2010, 10, 10)))
        p = Position(category=self.category, name='position-name', text='other text', active_from=utc_localize(datetime(2010, 9, 10)))
        tools.assert_raises(ValidationError, p.full_clean)

    def test_validation_fails_for_overlapping_positions3(self):
        Position.objects.create(category=self.category, name='position-name', text='some text', active_from=utc_localize(datetime(2010, 10, 10)))
        p = Position(category=self.category, name='position-name', text='other text', active_till=utc_localize(datetime(2010, 10, 11)))
        tools.assert_raises(ValidationError, p.full_clean)

    def test_validation_passes_for_nonoverlapping_positions(self):
        Position.objects.create(category=self.category, name='position-name', text='some text', active_till=utc_localize(datetime(2010, 10, 10, 10, 10, 10)))
        p = Position(category=self.category, name='position-name', text='other text', active_from=utc_localize(datetime(2010, 10, 10, 10, 10, 10)))
        p.full_clean()

    def test_validation_fails_for_incorrect_generic_fk(self):
        p = Position(category=self.category, name='position-name', target_ct=ContentType.objects.get_for_model(Position), target_id=123455)
        tools.assert_raises(ValidationError, p.full_clean)

    def test_render_position_without_target_renders_txt(self):
        p = Position.objects.create(category=self.category, name='position-name', text='some text')
        tools.assert_equals('some text', p.render(Context({}), NodeList(), ''))

    def test_render_position_with_invalid_target_returns_empty(self):
        target_ct = ContentType.objects.get_for_model(ContentType)
        invalid_id = ContentType.objects.aggregate(Max('id'))['id__max'] + 1

        p = Position.objects.create(category=self.category, name='position-name', text='some text', target_ct=target_ct, target_id=invalid_id)
        tools.assert_equals('', p.render(Context({}), NodeList(), ''))

    def test_get_active_position(self):
        p = Position.objects.create(category=self.category, name='position-name', text='some text')
        tools.assert_equals(p, Position.objects.get_active_position(self.category, 'position-name'))

    def test_get_active_position_nofallback(self):
        p = Position.objects.create(category=self.category, name='position-name', text='some text')
        tools.assert_equals(p, Position.objects.get_active_position(self.category, 'position-name', nofallback=True))

    def test_get_active_position_inherit(self):
        p = Position.objects.create(category=self.category, name='position-name', text='some text')
        tools.assert_equals(p, Position.objects.get_active_position(self.category_nested, 'position-name'))

    def test_get_active_position_inherit_nofallback(self):
        p = Position.objects.create(category=self.category, name='position-name', text='some text')
        tools.assert_false(Position.objects.get_active_position(self.category_nested, 'position-name', nofallback=True))

    def test_get_active_position_empty(self):
        tools.assert_false(Position.objects.get_active_position(self.category, 'position-name'))

    def test_active_till_past(self):
        p = Position.objects.create(category=self.category, name='position-name', text='some text', active_till=now()-timedelta(days=1))
        tools.assert_false(Position.objects.get_active_position(self.category, 'position-name'))

    def test_active_from_future(self):
        p = Position.objects.create(category=self.category, name='position-name', text='some text', active_from=now()+timedelta(days=1))
        tools.assert_false(Position.objects.get_active_position(self.category, 'position-name'))

    def test_active_till_future(self):
        p = Position.objects.create(category=self.category, name='position-name', text='some text', active_till=now()+timedelta(days=1))
        tools.assert_equals(p, Position.objects.get_active_position(self.category_nested, 'position-name'))

    def test_active_from_past(self):
        p = Position.objects.create(category=self.category, name='position-name', text='some text', active_from=now()-timedelta(days=1))
        tools.assert_equals(p, Position.objects.get_active_position(self.category_nested, 'position-name'))

    def test_active_from_till_match(self):
        p = Position.objects.create(category=self.category, name='position-name', text='some text',
                active_from=now()-timedelta(days=1),
                active_till=now()+timedelta(days=1),
            )
        tools.assert_equals(p, Position.objects.get_active_position(self.category_nested, 'position-name'))

    def test_active_from_till_no_match(self):
        p = Position.objects.create(category=self.category, name='position-name', text='some text',
                active_from=now()-timedelta(days=3),
                active_till=now()-timedelta(days=1),
            )
        tools.assert_false(Position.objects.get_active_position(self.category, 'position-name'))

    def test_more_positions_one_active(self):
        n = now()
        p1 = Position.objects.create(category=self.category, name='position-name', text='some text',
                active_from=n-timedelta(days=1),
            )
        p2 = Position.objects.create(category=self.category, name='position-name', text='some text', active_till=n-timedelta(days=1))
        tools.assert_equals(p1, Position.objects.get_active_position(self.category_nested, 'position-name'))

    def test_not_disabled(self):
        p = Position.objects.create(category=self.category, name='position-name', text='some text', disabled=False)
        tools.assert_equals(p, Position.objects.get_active_position(self.category, 'position-name'))

    def test_disabled(self):
        p = Position.objects.create(category=self.category, name='position-name', text='some text', disabled=True)
        tools.assert_false(Position.objects.get_active_position(self.category, 'position-name'))

    def test_position_with_broken_definition_dont_raise_big_500(self):
        p = Position.objects.create(category=self.category, name='position-name', text='{% load nonexistent_tags %}', disabled=False)
        tools.assert_equals('', p.render(Context({}), NodeList(), ''))

