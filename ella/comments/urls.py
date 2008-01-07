from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _

from ella.core.custom_urls import dispatcher


def comments_custom_urls(request, bits, context):
    from ella.comments.views import CommentFormPreview, new_comment, list_comments
    from ella.comments.forms import CommentForm

    if len(bits) == 2:
        if bits[0] == slugify(_('reply')) and bits[1].isdigit():
            return new_comment(request, context, reply=int(bits[1]))

    if len(bits) == 1:
        if bits[0] == slugify(_('preview')):
            comment_preview = CommentFormPreview(CommentForm)
            return comment_preview(request, context)
        elif bits[0] == slugify(_('new')):
            return new_comment(request, context)

    if len(bits) == 0:
        return list_comments(request, context)

    from django.http import Http404
    raise Http404

dispatcher.register(slugify(_('comments')), comments_custom_urls)

