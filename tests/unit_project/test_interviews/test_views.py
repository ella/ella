# -*- coding: utf-8 -*-
from datetime import datetime

from django.contrib.auth.models import User

from ella.interviews.models import Question, Answer
# register interviews' urls
from ella.interviews import register 
from ella.core.models import Placement

from unit_project.test_interviews import InterviewTestCase
from unit_project import template_loader


class InterviewViewTestCase(InterviewTestCase):
    def setUp(self):
        super(InterviewViewTestCase, self).setUp()
        self.placement = Placement.objects.create(
                category=self.interview.category,
                publishable=self.interview,
                publish_from=datetime.now(),
            )
        self.templates = template_loader.templates


    def tearDown(self):
        super(InterviewViewTestCase, self).tearDown()
        template_loader.templates = {}

class TestViews(InterviewViewTestCase):
    def test_custom_detail_context(self):
        self.templates['page/object.html'] = ''

        r = self.client.get(self.interview.get_absolute_url())

        self.assert_true('form' in r.context)
        self.assert_true('interviewees' in r.context)
        self.assert_equals([], r.context['interviewees'])

    def test_reply_lists_questions(self):
        u = User.objects.create(username='my_user')
        self.interviewee.user = u
        self.interviewee.save()
        q = Question.objects.create(interview=self.interview, content='What ?')

        url = self.interview.get_absolute_url() + 'reply/'
        r = self.client.get(url)

        self.assert_equals(200, r.status_code)


    def test_ask_works(self):
        self.templates['page/ask_preview.html'] = ''

        url = self.interview.get_absolute_url() + 'ask/'
        data = {'nickname': 'My nick', 'content': 'What ?'}
        r = self.client.post(url, data)

        self.assert_equals(200, r.status_code)
        self.assert_true('hash_field' in r.context)
        self.assert_true('hash_value' in r.context)
        
        data[r.context['hash_field']] = r.context['hash_value']
        data[r.context['stage_field']] = '2'

        r = self.client.post(url, data)
        self.assert_equals(302, r.status_code)

        self.assert_equals(1, Question.objects.all().count())
        q = Question.objects.all()[0]
        self.assert_equals(self.interview, q.interview)
        self.assert_equals(data['content'], q.content)
        self.assert_equals(data['nickname'], q.nickname)



