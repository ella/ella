from django.conf.urls.defaults import patterns, url
from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify

from ella.polls.models import Contest, Quiz
from ella.polls.views import poll_vote, survey_vote, quiz, contest, result_details, contest_conditions, contest_result
from ella.core.custom_urls import resolver


urlpatterns = patterns('',
    # POLL - vote to poll alt1
    url(r'^(?P<poll_id>\d+)/vote/$', poll_vote, name="polls_vote"),
    # POLL - vote to poll alt2
    url(r'^poll/(?P<poll_id>\d+)/vote/$', poll_vote, name="polls_poll_vote"),

    # SURVEY - vote to survey
    url(r'^survey/(?P<survey_id>\d+)/vote/$', survey_vote, name="polls_survey_vote"),

    # CONTEST - vote to contest
    #url(r'^contest/(?P<contest_id>\d+)/vote/$', contest_vote, name="polls_contest_vote"),
    # QUIZ - votes to quiz
    #url(r'^quiz/(?P<quiz_id>\d+)/vote/$', quiz_vote, name="polls_quiz_vote"),
)


resolver.register_custom_detail(Quiz, quiz)
resolver.register_custom_detail(Contest, contest)

resolver.register(
    patterns('',
        url('^%s/$' % slugify(_('results')), result_details, name='polls-quiz-result')
    ),
    model=Quiz
)
resolver.register(
    patterns('',
        url('^%s/$' % slugify(_('result')), contest_result, name='polls-contest-result'),
        url('^%s/$' % slugify(_('conditions')), contest_conditions, name='polls-contest-conditions')
    ),
    model=Contest
)


