# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from djangosanetesting import DatabaseTestCase

from unit_project.test_core import create_basic_categories, create_and_place_a_publishable

from ella.ellatagging import views

class TestTaggingViews(DatabaseTestCase):
    def setUp(self):
        try:
            import tagging
        except ImportError, e:
            raise self.SkipTest()

        from tagging.models import TaggedItem
        if not TaggedItem._meta.installed:
            raise self.SkipTest()

        super(TestTaggingViews, self).setUp()
        create_basic_categories(self)
        create_and_place_a_publishable(self)

    def test_get_tagged_publishables_returns_tagged_publishable(self):
        from tagging.models import Tag, TaggedItem

        Tag.objects.update_tags(self.publishable, 'tag1 tag2')
        self.assert_equals(2, TaggedItem.objects.count())

        t = Tag.objects.get(name='tag1')
        self.assert_equals([self.publishable], [p.target for p in views.get_tagged_publishables(t)])

    def test_get_tagged_publishables_doesnt_return_tagged_publishable_with_future_placement(self):
        from tagging.models import Tag, TaggedItem

        Tag.objects.update_tags(self.publishable, 'tag1 tag2')
        self.assert_equals(2, TaggedItem.objects.count())

        self.placement.publish_from = datetime.now() + timedelta(days=2)
        self.placement.save()

        t = Tag.objects.get(name='tag1')
        self.assert_equals([], list(views.get_tagged_publishables(t)))

    def test_get_tagged_publishables_returns_no_objects_when_none_tagged(self):
        from tagging.models import Tag
        t = Tag.objects.create(name='tag1')
        self.assert_equals([], list(views.get_tagged_publishables(t)))






