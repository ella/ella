from django.conf.urls.defaults import *
from django.utils.translation import ugettext_lazy as _

from ella.polls.models import Contest, Quiz
from ella.polls.views import poll_vote, quiz, contest, custom_result_details, cont_result, conditions
from ella.core.custom_urls import dispatcher


urlpatterns = patterns('',
    # POLL - vote to poll alt1
    url(r'^(?P<poll_id>\d+)/vote/$', poll_vote, name="polls_vote"),
    # POLL - vote to poll alt2
    url(r'^poll/(?P<poll_id>\d+)/vote/$', poll_vote, name="polls_poll_vote"),

    # CONTEST - vote to contest
    #url(r'^contest/(?P<contest_id>\d+)/vote/$', contest_vote, name="polls_contest_vote"),
    # QUIZ - votes to quiz
    #url(r'^quiz/(?P<quiz_id>\d+)/vote/$', quiz_vote, name="polls_quiz_vote"),
)


dispatcher.register_custom_detail(Quiz, quiz)
dispatcher.register_custom_detail(Contest, contest)
dispatcher.register(_('results'), custom_result_details, model=Quiz)
dispatcher.register(_('result'), cont_result, model=Contest)
dispatcher.register(_('conditions'), conditions, model=Contest)

