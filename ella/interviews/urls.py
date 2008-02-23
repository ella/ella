from django.utils.translation import ugettext
from django.template.defaultfilters import slugify

from ella.core.custom_urls import dispatcher
from ella.interviews.views import unanswered, reply, detail, QuestionForm, QuestionFormPreview
from ella.interviews.models import Interview

# add Interview-specific functionality
dispatcher.register(slugify(ugettext('unanswered')), unanswered, model=Interview)
dispatcher.register(slugify(ugettext('reply')), reply, model=Interview)
dispatcher.register(slugify(ugettext('ask')), QuestionFormPreview(QuestionForm),  model=Interview)

# override Interview's detail view
dispatcher.register_custom_detail(Interview, detail)
