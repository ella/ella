from django.conf.urls.defaults import *
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _ # lazy gettext works strange in case of urlpatterns (sometimes doesn't work)

from ella.answers.views import question_detail, question_list, question_preview, QuestionPreview, QuestionForm
from ella.answers.views import question_answer, AnswerForm, AnswerPreview

def _su(text):
    return slugify(_(text))

urlpatterns = patterns('',
    url(r'^$', question_list, name='answers_question_list'),
    # url(r'%s/$' % _su('preview'), question_preview, name='answers_question_preview'),
    url(r'%s/$' % _su('preview'), QuestionPreview(QuestionForm), name='answers_question_preview'),
    # url(r'%s/$' % _su('add question'), question_add, name='answers_question_add'),
    url(r'(?P<question_id>\d+)-(?P<question_slug>[a-z0-9-]+)/$', question_detail, name="answers_question_detail"),
    url(r'%s/(?P<question_id>\d+)/$' % _su('Answer question'), question_answer, name='answers_answer'),
    url(r'%s/(?P<question_id>\d+)/$' % _su('answer preview'), AnswerPreview(AnswerForm), name='answers_answer_preview'),
)
