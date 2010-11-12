# -*- coding: utf-8 -*-
from djangosanetesting import DestructiveDatabaseTestCase as DatabaseTestCase

from django.contrib import comments
from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify
from django.conf import settings

# register must be imported for custom urls
from ella.ellacomments import register
from ella.ellacomments.models import CommentOptionsObject, BannedIP

from unit_project import template_loader
from unit_project.test_core import create_basic_categories, create_and_place_a_publishable
from unit_project.test_ellacomments import create_comment

class CommentViewTestCase(DatabaseTestCase):
    def setUp(self):
        super(CommentViewTestCase, self).setUp()
        create_basic_categories(self)
        create_and_place_a_publishable(self)

    def get_url(self, *bits):
        url = [self.placement.get_absolute_url(), slugify(_('comments')), '/']
        if bits:
            url.append('/'.join(map(lambda x: slugify(_(str(x))), bits)))
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
        super(CommentViewTestCase, self).tearDown()
        template_loader.templates = {}

class TestCommentViewPagination(CommentViewTestCase):
    def setUp(self):
        super(TestCommentViewPagination, self).setUp()
        settings.COMMENTS_PAGINATE_BY = 3

    def tearDown(self):
        super(TestCommentViewPagination, self).tearDown()
        del settings._wrapped.COMMENTS_PAGINATE_BY

    def test_get_list_raises_404_on_incorrect_page_param(self):
        template_loader.templates['404.html'] = ''
        response = self.client.get(self.get_url(), {'p': 2})
        self.assert_equals(404, response.status_code)

    def test_get_list_returns_second_page_if_asked_to(self):
        template_loader.templates['page/comment_list.html'] = ''
        a = create_comment(self.publishable, self.publishable.content_type)
        d = create_comment(self.publishable, self.publishable.content_type)
        ab = create_comment(self.publishable, self.publishable.content_type, parent_id=a.pk)
        de = create_comment(self.publishable, self.publishable.content_type, parent_id=d.pk)
        def_ = create_comment(self.publishable, self.publishable.content_type, parent_id=de.pk)
        ac = create_comment(self.publishable, self.publishable.content_type, parent_id=a.pk)
        response = self.client.get(self.get_url(), {'p': 2})
        self.assert_equals(200, response.status_code)
        self.assert_equals([d, de, def_], list(response.context['comment_list']))

    def test_get_list_returns_first_page_with_no_params(self):
        template_loader.templates['page/comment_list.html'] = ''
        a = create_comment(self.publishable, self.publishable.content_type)
        d = create_comment(self.publishable, self.publishable.content_type)
        ab = create_comment(self.publishable, self.publishable.content_type, parent_id=a.pk)
        de = create_comment(self.publishable, self.publishable.content_type, parent_id=d.pk)
        def_ = create_comment(self.publishable, self.publishable.content_type, parent_id=de.pk)
        ac = create_comment(self.publishable, self.publishable.content_type, parent_id=a.pk)
        response = self.client.get(self.get_url())
        self.assert_equals(200, response.status_code)
        self.assert_equals([a, ab, ac], list(response.context['comment_list']))


class TestBannedIP(CommentViewTestCase):
    def setUp(self):
        super(TestBannedIP, self).setUp()
        self.ip_ban = BannedIP.objects.create(ip_address='127.0.0.1', reason='Test')

    def test_post_from_banned_ip_does_not_work(self):
        template_loader.templates['page/comment_form.html'] = ''
        form = comments.get_form()(target_object=self.publishable)
        response = self.client.post(self.get_url('new'), self.get_form_data(form))
        self.assert_equals(200, response.status_code)
        self.assert_equals(0, comments.get_model().objects.count())
        self.assert_true('ip_ban' in response.context)
        self.assert_equals(self.ip_ban, response.context['ip_ban'])

    def test_get_passes_ip_ban_to_template(self):
        template_loader.templates['page/comment_form.html'] = ''
        response = self.client.get(self.get_url('new'))
        self.assert_equals(200, response.status_code)
        self.assert_true('ip_ban' in response.context)
        self.assert_equals(self.ip_ban, response.context['ip_ban'])


class TestCommentModeration(CommentViewTestCase):
    def setUp(self):
        super(TestCommentModeration, self).setUp()
        self.opts = CommentOptionsObject.objects.create(target_ct=self.publishable.content_type, target_id=self.publishable.pk, premoderated=True)
        self.form = comments.get_form()(target_object=self.publishable)

    def test_premoderated_comments_are_not_public(self):
        response = self.client.post(self.get_url('new'), self.get_form_data(self.form))
        self.assert_equals(302, response.status_code)
        self.assert_equals(1, comments.get_model().objects.count())
        comment = comments.get_model().objects.all()[0]
        self.assert_equals(False, comment.is_public)

    def test_premoderated_comments_are_not_visible_in_listing(self):
        template_loader.templates['page/comment_list.html'] = ''
        response = self.client.post(self.get_url('new'), self.get_form_data(self.form))
        self.assert_equals(302, response.status_code)
        response = self.client.get(self.get_url())
        self.assert_true('comment_list' in response.context)
        self.assert_equals(0, len(response.context['comment_list']))

class TestCommentViews(CommentViewTestCase):

    def test_comments_urls_is_blocked(self):
        raise self.SkipTest()
#        template_loader.templates['404.html'] = ''
#        template_loader.templates['page/comment_list.html'] = ''
#        opts = CommentOptionsObject.objects.create(target_ct=self.publishable.content_type, target_id=self.publishable.pk, blocked=True)
#        response = self.client.get(self.get_url())
#        self.assert_equals(200, response.status_code)
#        self.assert_true('comment_list' in response.context)
#        self.assert_equals(0, len(response.context['comment_list']))

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
        self.assert_equals(str(c.pk), form.parent)

    def test_post_raises_404_for_non_existent_parent(self):
        template_loader.templates['404.html'] = ''
        response = self.client.get(self.get_url('new', 12345))
        self.assert_equals(404, response.status_code)

    def test_post_returns_bad_request_with_POST_and_no_data(self):
        template_loader.templates['comments/400-debug.html'] = ''
        template_loader.templates['page/comment_form.html'] = ''
        response = self.client.post(self.get_url('new'))
        self.assert_equals(400, response.status_code)

    def test_get_list_renders_correct_comments(self):
        template_loader.templates['page/comment_list.html'] = ''
        c = create_comment(self.publishable, self.publishable.content_type)
        c2 = create_comment(self.publishable, self.publishable.content_type)
        response = self.client.get(self.get_url())
        self.assert_equals(200, response.status_code)
        self.assert_equals([c, c2], list(response.context['comment_list']))

    def test_get_list_renders_correct_comments_including_tree_order(self):
        template_loader.templates['page/comment_list.html'] = ''
        a = create_comment(self.publishable, self.publishable.content_type)
        d = create_comment(self.publishable, self.publishable.content_type)
        ab = create_comment(self.publishable, self.publishable.content_type, parent_id=a.pk)
        de = create_comment(self.publishable, self.publishable.content_type, parent_id=d.pk)
        def_ = create_comment(self.publishable, self.publishable.content_type, parent_id=de.pk)
        ac = create_comment(self.publishable, self.publishable.content_type, parent_id=a.pk)
        response = self.client.get(self.get_url())
        self.assert_equals(200, response.status_code)
        self.assert_equals([a, ab, ac, d, de, def_], list(response.context['comment_list']))

    def test_get_list_renders_only_given_branch_if_asked_to(self):
        template_loader.templates['page/comment_list.html'] = ''
        a = create_comment(self.publishable, self.publishable.content_type)
        d = create_comment(self.publishable, self.publishable.content_type)
        ab = create_comment(self.publishable, self.publishable.content_type, parent_id=a.pk)
        de = create_comment(self.publishable, self.publishable.content_type, parent_id=d.pk)
        def_ = create_comment(self.publishable, self.publishable.content_type, parent_id=de.pk)
        ac = create_comment(self.publishable, self.publishable.content_type, parent_id=a.pk)
        response = self.client.get(self.get_url(), {'ids': a.pk})
        self.assert_equals(200, response.status_code)
        self.assert_equals([a, ab, ac], list(response.context['comment_list']))

    def test_get_list_renders_only_given_branches_if_asked_to(self):
        template_loader.templates['page/comment_list.html'] = ''
        a = create_comment(self.publishable, self.publishable.content_type)
        d = create_comment(self.publishable, self.publishable.content_type)
        ab = create_comment(self.publishable, self.publishable.content_type, parent_id=a.pk)
        de = create_comment(self.publishable, self.publishable.content_type, parent_id=d.pk)
        def_ = create_comment(self.publishable, self.publishable.content_type, parent_id=de.pk)
        ac = create_comment(self.publishable, self.publishable.content_type, parent_id=a.pk)
        response = self.client.get(self.get_url()+ '?ids=%s&ids=%s' % (a.pk, d.pk))
        self.assert_equals(200, response.status_code)
        self.assert_equals([a, ab, ac, d, de, def_], list(response.context['comment_list']))

