from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _

from ella.core.custom_urls import dispatcher


def comments_custom_urls(request, bits, context):
    from ella.comments.views import CommentFormPreview, new_comment, list_comments
    from ella.comments.forms import CommentForm

    if len(bits) == 1:
        if bits[0] == slugify(_('preview')):
            comment_preview = CommentFormPreview(CommentForm)
            return comment_preview(request)
        elif bits[0] == slugify(_('new')):
            return new_comment(request, context['object'])

    if len(bits) == 0:
        return list_comments(request, context['object'])

    from django.http import Http404
    raise Http404

def register_custom_urls():
    """register all custom urls"""
    dispatcher.register(slugify(_('comments')), comments_custom_urls)


