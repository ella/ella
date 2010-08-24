# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from djangosanetesting import DatabaseTestCase

from django.core.urlresolvers import reverse
from django.conf import settings
from django.template import NodeList, Context
from django.contrib.auth.models import User

from ella.polls.models import Poll, Question, Choice, Vote
from ella.polls import views, conf

# FIXME hack alert - we are calling the registration here, it should be dealt
# with in the project itself somehow
#from ella.polls import urls

from unit_project.test_core import create_basic_categories
from unit_project import template_loader


def create_poll(case):
    """
    Creates one poll with question and its choices
    """
    case.question = Question.objects.create(
        question = u'Some\nquestion', 
    )
    case.poll = Poll.objects.create(
        title = u'Some Poll',
        text_announcement = u'Some\nannouncement\ntext',
        text = u'Some\ntext',
        text_results = u'Some\ntext\nwith\nresults',
        active_from = datetime.now() - timedelta(1),
        active_till = datetime.now() + timedelta(1),
        question = case.question, 
    )
    case.choiceA = Choice.objects.create(question=case.question, choice='A')
    case.choiceB = Choice.objects.create(question=case.question, choice='B')
    case.choiceC = Choice.objects.create(question=case.question, choice='C')


def build_request(user=None, session={}, cookies={}, ip_address=None):
    """
    Returns request object with useful attributes
    """
    from django.http import HttpRequest
    from django.contrib.auth.middleware import LazyUser
    request = HttpRequest()
    # Session and cookies
    request.session = session
    request.COOKIES = cookies
    # User
    request.__class__.user = user or LazyUser()
    # Meta
    request.META['REMOTE_ADDR'] = ip_address or '0.0.0.0'
    return request

class TestPollBox(DatabaseTestCase):
    def setUp(self):
        super(TestPollBox, self).setUp()
        create_poll(self)
        self.orgig_double_render = getattr(settings, 'DOUBLE_RENDER', False)

    def tearDown(self):
        super(TestPollBox, self).tearDown()
        settings.DOUBLE_RENDER = self.orgig_double_render

    def test_state_is_set_for_poll_box(self):
        user = User.objects.create(username='stickyfingaz')
        Vote.objects.create(poll=self.poll, user=user)
        box = Poll.box_class(self.poll, 'name', NodeList())
        box.prepare(Context({'request': build_request(user=user)}))
        self.assert_equals(
            conf.USER_ALLREADY_VOTED, 
            box.state)

    def test_state_is_not_set_for_poll_box_in_first_of_double_renders(self):
        settings.DOUBLE_RENDER = True
        user = User.objects.create(username='stickyfingaz')
        Vote.objects.create(poll=self.poll, user=user)
        box = Poll.box_class(self.poll, 'name', NodeList())
        box.prepare(Context({'request': build_request(user=user)}))
        self.assert_equals(
            None,
            box.state)

    def test_state_is_set_for_poll_box_in_second_of_double_renders(self):
        settings.DOUBLE_RENDER = True
        user = User.objects.create(username='stickyfingaz')
        Vote.objects.create(poll=self.poll, user=user)
        box = Poll.box_class(self.poll, 'name', NodeList())
        box.prepare(Context({'request': build_request(user=user), 'SECOND_RENDER': True}))
        self.assert_equals(
            conf.USER_ALLREADY_VOTED,
            box.state)


class TestPolls(DatabaseTestCase):

    def setUp(self):
        super(TestPolls, self).setUp()
        create_poll(self)

    def tearDown(self):
        super(TestPolls, self).tearDown()
        #template_loader.templates = {}

    def test_poll_get_total_votes_no_votes(self):
        self.assert_equals(0, self.poll.get_total_votes())

    def test_poll_get_total_votes(self):
        user = User.objects.create(username='stickyfingaz')
        self.choiceA.votes = 1
        self.choiceA.save()
        self.choiceB.votes = 3
        self.choiceB.save()
        self.assert_equals(4, self.poll.get_total_votes())

    def test_check_vote_annonymous_user_not_yet_voted(self):
        self.assert_equals(
            conf.USER_NOT_YET_VOTED, 
            views.poll_check_vote(build_request(ip_address='127.0.0.1'), self.poll))

    def test_check_vote_authetnticated_user_not_yet_voted(self):
        user = User.objects.create(username='stickyfingaz')
        self.assert_equals(
            conf.USER_NOT_YET_VOTED, 
            views.poll_check_vote(build_request(user=user), self.poll))

    def test_check_vote_annonymous_user_allready_voted_by_vote_object(self):
        Vote.objects.create(poll=self.poll, ip_address='127.0.0.1')
        self.assert_equals(
            conf.USER_ALLREADY_VOTED, 
            views.poll_check_vote(build_request(ip_address='127.0.0.1'), self.poll))

    def test_check_vote_authetnticated_user_allready_voted_by_vote_object(self):
        user = User.objects.create(username='stickyfingaz')
        Vote.objects.create(poll=self.poll, user=user)
        self.assert_equals(
            conf.USER_ALLREADY_VOTED, 
            views.poll_check_vote(build_request(user=user), self.poll))

    def test_check_vote_annonymous_user_allready_voted_by_cookies(self):
        cookies = {conf.POLL_COOKIE_NAME: ','.join(str(self.poll.pk))}
        self.assert_equals(
            conf.USER_ALLREADY_VOTED,
            views.poll_check_vote(build_request(cookies=cookies), self.poll))

    def test_check_vote_authetnticated_user_allready_voted_by_session(self):
        user = User.objects.create(username='stickyfingaz')
        session = {conf.POLL_COOKIE_NAME: [self.poll.pk]}
        self.assert_equals(
            conf.USER_ALLREADY_VOTED, 
            views.poll_check_vote(build_request(user=user, session=session), self.poll))

    def test_poll_vote(self):
        user = User.objects.create(username='stickyfingaz')
        choice = self.choiceA
        self.poll.vote(choice=choice, user=user)
        self.assert_equals(1, self.poll.get_total_votes())


    ### View testing

    def test_view_poll_vote_method_not_allowed_error(self):
        vote_url = reverse('polls_vote', kwargs={'poll_id': self.poll.pk})
        response = self.client.get(vote_url)
        self.assert_equals(405, response.status_code)

    def test_view_poll_vote_no_choice_error(self):
        vote_url = reverse('polls_vote', kwargs={'poll_id': self.poll.pk})
        response = self.client.post(vote_url)
        self.assert_equals(302, response.status_code)
        self.assert_equals(0, self.poll.get_total_votes())
        self.assert_equals([self.poll.pk], self.client.session.get(conf.POLL_NO_CHOICE_COOKIE_NAME, []))

    def test_view_poll_vote_success(self):
        vote_url = reverse('polls_vote', kwargs={'poll_id': self.poll.pk})
        response = self.client.post(vote_url, {'choice': self.choiceB.pk})
        self.assert_equals(302, response.status_code)
        self.assert_equals(1, self.poll.get_total_votes())
        self.assert_equals([self.poll.pk], self.client.session.get(conf.POLL_JUST_VOTED_COOKIE_NAME, [])) 
