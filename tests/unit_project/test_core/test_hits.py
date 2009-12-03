# -*- coding: utf-8 -*-
from djangosanetesting import DatabaseTestCase

from ella.core.models import HitCount
from ella.articles.models import Article

from unit_project.test_core import create_basic_categories, create_and_place_a_publishable, create_and_place_more_publishables

class TestHitCounts(DatabaseTestCase):
    def setUp(self):
        super(TestHitCounts, self).setUp()
        create_basic_categories(self)
        create_and_place_a_publishable(self)

    def test_hitcount_is_created_with_placement(self):
        self.assert_equals(1, HitCount.objects.count())
        hc = HitCount.objects.all()[0]
        self.assert_equals(self.placement, hc.placement)
        self.assert_equals(0, hc.hits)

    def test_hit_increases_hit_count(self):
        HitCount.objects.hit(self.placement)
        hc = HitCount.objects.all()[0]
        self.assert_equals(1, hc.hits)

    def test_hit_creates_hitcount_if_not_exist(self):
        HitCount.objects.all().delete()
        HitCount.objects.hit(self.placement)
        self.assert_equals(1, HitCount.objects.count())
        hc = HitCount.objects.all()[0]
        self.assert_equals(1, hc.hits)

class TestTopObjects(DatabaseTestCase):
    def setUp(self):
        super(TestTopObjects, self).setUp()
        create_basic_categories(self)
        create_and_place_a_publishable(self)
        create_and_place_more_publishables(self)

    def test_top_objects(self):
        HitCount.objects.hit(self.placement)
        HitCount.objects.hit(self.placement)
        HitCount.objects.hit(self.placements[0])
        self.assert_equals([self.placement, self.placements[0]], [hc.placement for hc in HitCount.objects.get_top_objects(2)])

    def test_top_objects_for_specific_model(self):
        HitCount.objects.hit(self.placement)
        HitCount.objects.hit(self.placement)
        HitCount.objects.hit(self.placements[0])
        self.assert_equals([self.placement, self.placements[0]], [hc.placement for hc in HitCount.objects.get_top_objects(2, mods=[Article])])
