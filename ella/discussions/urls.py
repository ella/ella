from ella.core.custom_urls import dispatcher
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _
from ella.discussions.models import Topic
from ella.discussions.views import topic, topicthread, create_thread, post_reply
from ella.oldcomments.views import CommentFormPreview
from ella.oldcomments.forms import CommentForm

def discussion_custom_urls(request, bits, context):
    if len(bits) == 3:
        if bits[1] == slugify(_('comments')) and bits[2] == slugify(_('preview')):
            comment_preview = CommentFormPreview(CommentForm)
            return comment_preview(request, context)
        elif bits[1] == slugify(_('comments')) and bits[2] == slugify(_('new')):
            return post_reply(request, context, reply = None, thread = bits[0])
    if len(bits) == 4:
        if bits[2] == slugify(_('reply')) and bits[3].isdigit():
            return post_reply(request, context, reply = int(bits[3]), thread = bits[0])

    return topicthread(request, bits, context)

#dispatcher.register(slugify(_('ask')), ask_question, model=Topic)
#dispatcher.register(slugify(_('question')), question, model=Topic)
dispatcher.register(slugify(_('create thread')), create_thread)
dispatcher.register_custom_detail(Topic, topic)
dispatcher.register(slugify(_('posts')), discussion_custom_urls)



