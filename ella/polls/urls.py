from django.conf.urls.defaults import *
from ella.polls.views import *

urlpatterns = patterns('',
    # POLL - vote to poll alt1
    url(r'^(?P<poll_id>\d+)/vote/$', poll_vote, name="polls_vote"),
    # POLL - vote to poll alt2
    url(r'^poll/(?P<poll_id>\d+)/vote/$', poll_vote, name="polls_poll_vote"),
    # CONTEST - vote to contest
    url(r'^contest/(?P<contest_id>\d+)/vote/$', contest_vote, name="polls_contest_vote"),
    # QUIZ - votes to quiz
    url(r'^quiz/(?P<quiz_id>\d+)/vote/$', quiz_vote, name="polls_quiz_vote"),
)

