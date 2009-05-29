# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from djangosanetesting import UnitTestCase

from ella.interviews.models import Interview, Question, Answer

from unit_project.test_interviews import InterviewTestCase


class TestInterviewModels(InterviewTestCase):
    def test_has_replies_returns_false_when_no_replies(self):
        self.assert_equals(False, self.interview.has_replies())

    def test_unanswered_questions_empty_with_no_questions(self):
        self.assert_equals([], list(self.interview.unanswered_questions()))

    def test_unanswered_questions(self):
        q = Question.objects.create(interview=self.interview, content='What ?')
        self.assert_equals([q], list(self.interview.unanswered_questions()))

    def test_unanswered_questions_empty_with_only_answered_questions(self):
        q = Question.objects.create(interview=self.interview, content='What ?')
        a = Answer.objects.create(interviewee=self.interviewee, question=q, content='That !')
        self.assert_equals([], list(self.interview.unanswered_questions()))


class TestInterviewModel(UnitTestCase):
    def setUp(self):
        super(TestInterviewModel, self).setUp()
        now = datetime.now()
        day = timedelta(days=1)
        self.interview = Interview(
                title='First Interview',
                slug='first-interview',
                description='Some description',
                reply_from=now-day,
                reply_to=now+day,
                ask_from=now-day,
                ask_to=now+day,
                content='Some Text content',
            )

    def test_ask_indicators_when_active(self):
        self.assert_equals(True, self.interview.asking_started())
        self.assert_equals(False, self.interview.asking_ended())
        self.assert_equals(True, self.interview.can_ask())

    def test_ask_indicators_when_not_yet_active(self):
        now = datetime.now()
        day = timedelta(days=1)
        self.interview.ask_from = now+(day/2)
        self.assert_equals(False, self.interview.asking_started())
        self.assert_equals(False, self.interview.asking_ended())
        self.assert_equals(False, self.interview.can_ask())

    def test_ask_indicators_when_already_inactive(self):
        now = datetime.now()
        day = timedelta(days=1)
        self.interview.ask_to = now-(day/2)
        self.assert_equals(True, self.interview.asking_started())
        self.assert_equals(True, self.interview.asking_ended())
        self.assert_equals(False, self.interview.can_ask())

    def test_reply_indicators_when_active(self):
        self.assert_equals(True, self.interview.replying_started())
        self.assert_equals(False, self.interview.replying_ended())
        self.assert_equals(True, self.interview.can_reply())

    def test_reply_indicators_when_not_yet_active(self):
        now = datetime.now()
        day = timedelta(days=1)
        self.interview.reply_from = now+(day/2)
        self.assert_equals(False, self.interview.replying_started())
        self.assert_equals(False, self.interview.replying_ended())
        self.assert_equals(False, self.interview.can_reply())

    def test_reply_indicators_when_already_inactive(self):
        now = datetime.now()
        day = timedelta(days=1)
        self.interview.reply_to = now-(day/2)
        self.assert_equals(True, self.interview.replying_started())
        self.assert_equals(True, self.interview.replying_ended())
        self.assert_equals(False, self.interview.can_reply())

