from django.utils.translation import ugettext
from django.template.defaultfilters import slugify
from django.conf.urls.defaults import patterns, url

from ella.core.custom_urls import resolver
from ella.interviews.views import unanswered, reply, detail, QuestionForm, QuestionFormPreview, list_questions
from ella.interviews.models import Interview

urlpatterns = patterns('',
    url('^%s/$' % slugify(ugettext('unanswered')), unanswered, name='interview-unanswered'),
    url('^%s/$' % slugify(ugettext('reply')), list_questions, {}, name='interview-list-questions'),
    url('^%s/(\d+)/$' % slugify(ugettext('reply')), reply, {}, name='interview-reply'),
    url('^%s/$' % slugify(ugettext('ask')), QuestionFormPreview(QuestionForm), name='interview-ask'),
)
# add Interview-specific functionality
resolver.register(urlpatterns, model=Interview)

# override Interview's detail view
resolver.register_custom_detail(Interview, detail)
