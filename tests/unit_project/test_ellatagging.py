# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from django.core.urlresolvers import reverse

from djangosanetesting import DatabaseTestCase

from ella.ellatagging import views
from ella.core.models import Publishable

from unit_project.test_core import create_basic_categories, create_and_place_a_publishable
from unit_project import template_loader

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

    def tearDown(self):
        super(TestTaggingViews, self).tearDown()
        template_loader.templates = {}

    def test_get_tagged_publishables_returns_tagged_publishable(self):
        from tagging.models import Tag, TaggedItem

        Tag.objects.update_tags(self.only_publishable, 'tag1 tag2')
        self.assert_equals(2, TaggedItem.objects.count())

        t = Tag.objects.get(name='tag1')
        self.assert_equals([self.publishable], [p.target for p in views.get_tagged_publishables(t)])

    def test_get_tagged_publishables_doesnt_return_tagged_publishable_with_future_placement(self):
        from tagging.models import Tag, TaggedItem

        Tag.objects.update_tags(self.only_publishable, 'tag1 tag2')
        self.assert_equals(2, TaggedItem.objects.count())

        self.placement.publish_from = datetime.now() + timedelta(days=2)
        self.placement.save()

        t = Tag.objects.get(name='tag1')
        self.assert_equals([], list(views.get_tagged_publishables(t)))

    def test_get_tagged_publishables_returns_no_objects_when_none_tagged(self):
        from tagging.models import Tag
        t = Tag.objects.create(name='tag1')
        self.assert_equals([], list(views.get_tagged_publishables(t)))

    def test_tagged_publishables_view(self):
        from tagging.models import Tag, TaggedItem

        Tag.objects.update_tags(self.only_publishable, 'tag1 tag2')
        self.assert_equals(2, TaggedItem.objects.count())

        t = Tag.objects.get(name='tag1')
        url = reverse('tag_list', kwargs={'tag':'tag1'})
        template_loader.templates['page/tagging/listing.html'] = ''
        response = self.client.get(url)

        self.assert_equals([self.publishable], [p.target for p in response.context['object_list']])
        self.assert_equals(t, response.context['tag'])

