# -*- coding: utf-8 -*-
from django.test import TestCase

from nose import tools

from django import template

from test_ella.test_core import create_basic_categories, create_and_place_a_publishable
from test_ella.test_ellacomments import create_comment

class TestTemplateTags(TestCase):
    def setUp(self):
        super(TestTemplateTags, self).setUp()
        create_basic_categories(self)
        create_and_place_a_publishable(self)

    def test_comment_count_for_article_is_picked_up_through_article(self):
        create_comment(self.publishable, self.publishable.content_type)
        t = template.Template('''{% load ellacomments_tags %}{% get_comment_count for obj as var_name%}{{ var_name }}''')
        tools.assert_equals('1', t.render(template.Context({'obj': self.publishable})))

    def test_comment_count_for_article_is_picked_up_through_publishable(self):
        create_comment(self.publishable, self.publishable.content_type)
        t = template.Template('''{% load ellacomments_tags %}{% get_comment_count for obj as var_name%}{{ var_name }}''')
        tools.assert_equals('1', t.render(template.Context({'obj': self.only_publishable})))

    def test_comment_list_for_article_is_picked_up_through_article(self):
        create_comment(self.publishable, self.publishable.content_type)
        t = template.Template('''{% load ellacomments_tags %}{% get_comment_list for obj as var_name%}{{ var_name|length }}''')
        tools.assert_equals('1', t.render(template.Context({'obj': self.publishable})))

    def test_comment_list_for_article_is_picked_up_through_publishable(self):
        create_comment(self.publishable, self.publishable.content_type)
        t = template.Template('''{% load ellacomments_tags %}{% get_comment_list for obj as var_name%}{{ var_name|length }}''')
        tools.assert_equals('1', t.render(template.Context({'obj': self.only_publishable})))

    def test_default_comment_options_for_article(self):
        create_comment(self.publishable, self.publishable.content_type)
        t = template.Template('''{% load ellacomments_tags %}{% get_comment_options for obj as opts %}{% if not opts.blocked %}XX{% endif %}''')
        tools.assert_equals(u'XX', t.render(template.Context({'obj': self.only_publishable})))

    def test_block_comments_for_article(self):
        from ella.ellacomments.models import CommentOptionsObject
        opts = CommentOptionsObject.objects.create(target_ct=self.publishable.content_type, target_id=self.publishable.pk, blocked=True)
        t = template.Template('''{% load ellacomments_tags %}{% get_comment_options for obj as opts %}{% if opts.blocked %}XX{% endif %}''')
        tools.assert_equals(u"XX", t.render(template.Context({'obj': self.publishable})))
