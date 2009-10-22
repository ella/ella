# -*- coding: utf-8 -*-
from djangosanetesting import DatabaseTestCase

from django.contrib.auth.models import AnonymousUser
from django.http import QueryDict

from ella.ellacomments.views import post_comment

from unit_project import template_loader
from unit_project.test_core import create_basic_categories, create_and_place_a_publishable
from unit_project.test_ellacomments import create_comment

class FakeRequest(object):
    def __init__(self, **kwargs):
        self.user = AnonymousUser()
        self.META = {}
        self.method = 'GET'
        self.GET = QueryDict('')
        self.POST = QueryDict('')

        for (k, v) in kwargs.items():
            setattr(self, k, v)

class TestCommentViews(DatabaseTestCase):
    def setUp(self):
        super(TestCommentViews, self).setUp()
        create_basic_categories(self)
        create_and_place_a_publishable(self)
        self.context = {
                'placement' : self.placement,
                'object' : self.publishable,
                'category' : self.placement.category,
                'content_type_name' : unicode(self.publishable._meta.verbose_name_plural),
                'content_type' : self.publishable.content_type 
            }

    def tearDown(self):
        super(TestCommentViews, self).tearDown()
        template_loader.templates = {}

    def test_post_renders_comment_form_on_get(self):
        template_loader.templates['page/comment_form.html'] = '{{form.target_object}}'
        response = post_comment(FakeRequest(), self.context, None)
        self.assert_equals(200, response.status_code)
        self.assert_equals(unicode(self.publishable), response.content)

    def test_post_passes_parent_on_get_to_template_if_specified(self):
        template_loader.templates['page/comment_form.html'] = '{{parent.pk}}'
        c = create_comment(self.publishable, self.publishable.content_type)
        response = post_comment(FakeRequest(), self.context, c)
        self.assert_equals(200, response.status_code)
        self.assert_equals(unicode(c.pk), response.content)

    def test_post_returns_bad_request_with_POST_and_no_data(self):
        template_loader.templates['page/comment_form.html'] = '{{parent.pk}}'
        response = post_comment(FakeRequest(method='POST'), self.context, None)
        self.assert_equals(400, response.status_code)

