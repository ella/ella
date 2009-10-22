# -*- coding: utf-8 -*-
from djangosanetesting import DatabaseTestCase

from django.contrib import comments
from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify

from unit_project import template_loader
from unit_project.test_core import create_basic_categories, create_and_place_a_publishable
from unit_project.test_ellacomments import create_comment

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

    def get_url(self, *bits):
        url = [self.placement.get_absolute_url(), slugify(_('comments')), '/']
        if bits:
            url.append('/'.join(map(lambda x: slugify(_(x)), bits)))
            url.append('/')

        return ''.join(url)

    def get_form_data(self, form, **kwargs):
        out = {
            'name': 'Honza',
            'email': 'honza.kral@gmail.com',
            'url': '',
            'comment': 'I like this App',
        }
        out.update(kwargs)
        out['parent'] = form.parent and form.parent or ''
        out.update(form.generate_security_data())
        return out

    def tearDown(self):
        super(TestCommentViews, self).tearDown()
        template_loader.templates = {}

    def test_post_works_for_correct_data(self):
        form = comments.get_form()(target_object=self.publishable)
        response = self.client.post(self.get_url('new'), self.get_form_data(form))
        self.assert_equals(302, response.status_code)
        self.assert_equals(1, comments.get_model().objects.count())

    def test_post_works_for_correct_data_with_parent(self):
        c = create_comment(self.publishable, self.publishable.content_type)
        form = comments.get_form()(target_object=self.publishable, parent=c.pk)
        response = self.client.post(self.get_url('new'), self.get_form_data(form))
        self.assert_equals(302, response.status_code)
        self.assert_equals(2, comments.get_model().objects.count())
        child = comments.get_model().objects.exclude(pk=c.pk)[0]
        self.assert_equals(c, child.parent)

    def test_post_renders_comment_form_on_get(self):
        template_loader.templates['page/comment_form.html'] = ''
        response = self.client.get(self.get_url('new'))
        self.assert_equals(200, response.status_code)
        self.assert_true('form' in response.context)
        form =  response.context['form']
        self.assert_equals(self.publishable, form.target_object)

    def test_post_passes_parent_on_get_to_template_if_specified(self):
        template_loader.templates['page/comment_form.html'] = ''
        c = create_comment(self.publishable, self.publishable.content_type)
        response = self.client.get(self.get_url('new', c.pk))
        self.assert_equals(200, response.status_code)
        self.assert_true('parent' in response.context)
        self.assert_equals(c, response.context['parent'])
        form =  response.context['form']
        self.assert_equals(c.pk, form.parent)

    def test_post_raises_404_for_non_existent_parent(self):
        template_loader.templates['404.html'] = ''
        response = self.client.get(self.get_url('new', 12345))
        self.assert_equals(404, response.status_code)

    def test_post_returns_bad_request_with_POST_and_no_data(self):
        template_loader.templates['page/comment_form.html'] = '{{parent.pk}}'
        response = self.client.post(self.get_url('new'))
        self.assert_equals(400, response.status_code)

