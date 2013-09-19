# -*- coding: utf-8 -*-
from datetime import timedelta, datetime
import pytz

from test_ella.cases import RedisTestCase as TestCase
from django.contrib.sites.models import Site
from django.contrib.redirects.models import Redirect
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError

from ella.core.models import Category, Publishable
from ella.core import signals
from ella.core.management import generate_publish_signals
from ella.utils import timezone

from nose import tools, SkipTest

from test_ella.test_core import create_basic_categories, create_and_place_a_publishable, default_time

class PublishableTestCase(TestCase):
    def setUp(self):
        super(PublishableTestCase, self).setUp()
        create_basic_categories(self)
        create_and_place_a_publishable(self)

class TestLastUpdated(PublishableTestCase):
    def test_last_updated_moved_if_default(self):
        now = timezone.now()
        self.publishable.publish_from = now
        self.publishable.save(force_update=True)
        tools.assert_equals(now, self.publishable.last_updated)

    def test_last_updated_isnt_moved_if_changed(self):
        now = timezone.now()
        self.publishable.last_updated = now + timedelta(days=1)
        self.publishable.publish_from = now
        self.publishable.save(force_update=True)
        tools.assert_equals(now + timedelta(days=1), self.publishable.last_updated)

class TestPublishableHelpers(PublishableTestCase):
    def test_url(self):
        tools.assert_equals('/nested-category/2008/1/10/first-article/', self.publishable.get_absolute_url())

    def test_tz_aware_url(self):
        if not timezone.use_tz:
            raise SkipTest()
        utc = pytz.timezone('UTC')
        self.publishable.publish_from = datetime(2008, 1, 9, 23, 50, 0, tzinfo=utc)
        tools.assert_equals('/nested-category/2008/1/10/first-article/', self.publishable.get_absolute_url())

    def test_domain_url(self):
        tools.assert_equals('http://example.com/nested-category/2008/1/10/first-article/', self.publishable.get_domain_url())

    def test_app_data(self):
        tools.assert_equals({}, self.publishable.app_data)
        self.publishable.app_data['core'] = 'testing'
        self.publishable.save()

        p = self.publishable.content_type.get_object_for_this_type(pk=self.publishable.pk)
        tools.assert_equals({'core': 'testing'}, self.publishable.app_data)

    def test_saving_base_publishable_does_not_update_content_type(self):
        publishable_ct = ContentType.objects.get_for_model(Publishable)
        current_ct = self.publishable.content_type
        tools.assert_not_equals(publishable_ct, current_ct)

        p = Publishable.objects.get(pk=self.publishable.pk)
        p.save()
        tools.assert_equals(current_ct, p.content_type)


class TestRedirects(PublishableTestCase):
    def test_url_change_creates_redirect(self):
        self.publishable.slug = 'old-article-new-slug'
        self.publishable.save()
        tools.assert_equals(1, Redirect.objects.count())
        r = Redirect.objects.all()[0]

        tools.assert_equals('/nested-category/2008/1/10/first-article/', r.old_path)
        tools.assert_equals('/nested-category/2008/1/10/old-article-new-slug/', r.new_path)
        tools.assert_equals(self.site_id, r.site_id)

    def test_url_change_updates_existing_redirects(self):
        r = Redirect.objects.create(site_id=self.site_id, new_path='/nested-category/2008/1/10/first-article/', old_path='some-path')
        self.publishable.slug = 'old-article-new-slug'
        self.publishable.save()
        tools.assert_equals(2, Redirect.objects.count())
        r = Redirect.objects.get(pk=r.pk)

        tools.assert_equals('some-path', r.old_path)
        tools.assert_equals('/nested-category/2008/1/10/old-article-new-slug/', r.new_path)
        tools.assert_equals(self.site_id, r.site_id)

    def test_ability_to_place_back_and_forth(self):
        self.publishable.slug = 'old-article-new-slug'
        self.publishable.save()
        self.publishable.slug = 'first-article'
        self.publishable.save()
        self.publishable.slug = 'old-article-new-slug'
        self.publishable.save()


class TestUrl(PublishableTestCase):
    def test_home_url(self):
        self.publishable.category = self.category
        self.publishable.save()
        tools.assert_equals('/2008/1/10/first-article/', self.publishable.get_absolute_url())

    def test_url(self):
        tools.assert_equals('/nested-category/2008/1/10/first-article/', self.publishable.get_absolute_url())

    def test_url_on_other_site(self):
        site = Site.objects.create(
            name='some site',
            domain='not-example.com'
        )

        category = Category.objects.create(
            title=u"再见 category",
            description=u"example testing category, second site",
            site=site,
            slug=u'zai-jian-category',
        )

        self.publishable.category = category
        self.publishable.publish_from = default_time
        self.publishable.save()

        tools.assert_equals(u'http://not-example.com/2008/1/10/first-article/', self.publishable.get_absolute_url())

    def test_unique_url_validation(self):
        self.publishable.pk = None
        tools.assert_raises(ValidationError, self.publishable.full_clean)

    def test_url_is_tested_for_published_objects_only(self):
        self.publishable.pk = None
        self.publishable.published = False
        self.publishable.full_clean()


class TestSignals(TestCase):
    def setUp(self):
        super(TestSignals, self).setUp()
        signals.content_published.connect(self.publish)
        signals.content_unpublished.connect(self.unpublish)
        self._signal_clear()
        create_basic_categories(self)
        create_and_place_a_publishable(self)

    def tearDown(self):
        super(TestSignals, self).tearDown()
        signals.content_published.disconnect(self.publish)
        signals.content_unpublished.disconnect(self.unpublish)

    def _signal_clear(self):
        self.publish_received = []
        self.unpublish_received = []

    # signal handlers
    def publish(self, **kwargs):
        self.publish_received.append(kwargs)

    def unpublish(self, **kwargs):
        self.unpublish_received.append(kwargs)

    def test_publishable_is_announced_on_save(self):
        tools.assert_true(self.publishable.announced)
        tools.assert_equals(1, len(self.publish_received))
        tools.assert_equals(0, len(self.unpublish_received))
        tools.assert_equals(self.publishable, self.publish_received[0]['publishable'])

    def test_unpublish_sent_when_takedown_occurs(self):
        self._signal_clear()
        self.publishable.published = False
        self.publishable.save()
        tools.assert_false(self.publishable.announced)
        tools.assert_equals(0, len(self.publish_received))
        tools.assert_equals(1, len(self.unpublish_received))
        tools.assert_equals(self.publishable, self.unpublish_received[0]['publishable'])

    def test_generate_doesnt_issue_signal_twice(self):
        self._signal_clear()
        generate_publish_signals()
        tools.assert_equals(0, len(self.publish_received))
        tools.assert_equals(0, len(self.unpublish_received))

    def test_generate_picks_up_on_takedown(self):
        self.publishable.publish_to = timezone.now() + timedelta(days=1)
        self.publishable.save()
        self._signal_clear()
        generate_publish_signals(timezone.now() + timedelta(days=1, seconds=2))
        tools.assert_equals(0, len(self.publish_received))
        tools.assert_equals(1, len(self.unpublish_received))
        tools.assert_equals(self.publishable, self.unpublish_received[0]['publishable'].target)

    def test_generate_picks_up_on_publish(self):
        self.publishable.publish_from = timezone.now() + timedelta(days=1)
        self.publishable.save()
        self._signal_clear()
        generate_publish_signals(timezone.now() + timedelta(days=1, seconds=2))
        tools.assert_equals(1, len(self.publish_received))
        tools.assert_equals(0, len(self.unpublish_received))
        tools.assert_equals(self.publishable, self.publish_received[0]['publishable'].target)

