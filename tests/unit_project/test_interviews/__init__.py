# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from djangosanetesting import DatabaseTestCase

from ella.interviews.models import Interview, Interviewee

from unit_project.test_core import create_basic_categories

class InterviewTestCase(DatabaseTestCase):
    def setUp(self):
        super(InterviewTestCase, self).setUp()
        create_basic_categories(self)

        self.interviewee = Interviewee(
                slug='interviewee1',
                name='Some Interviewee',
            )
        self.interviewee.save()

        now = datetime.now()
        day = timedelta(days=1)
        self.interview = Interview(
                category=self.category,
                title='First Interview',
                slug='first-interview',
                description='Some description',
                reply_from=now-day,
                reply_to=now+day,
                ask_from=now-day,
                ask_to=now+day,
                content='Some Text content',
            )
        self.interview.save()
        self.interview.interviewees.add(self.interviewee)


