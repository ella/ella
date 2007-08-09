from django.contrib.formtools.preview import FormPreview

from ella.core.custom_urls import dispatcher
from ella.comments.forms import CommentForm

from django.shortcuts import get_object_or_404
from ella.core.cache import get_cached_object_or_404

from django.contrib.contenttypes.models import ContentType

from django.http import HttpResponseRedirect

class CommentFormPreview(FormPreview):
    def done(self, request, cleaned_data):
        CommentForm(request.POST).save(
                other_values={'ip_address': request.META['REMOTE_ADDR']})
        # TODO: add better redirect (object.get_absolute_url)
        ct = get_object_or_404(ContentType, pk=cleaned_data['target_ct'].id)
        target = get_object_or_404(ct.model_class(), pk=cleaned_data['target_id'])
        if hasattr(target, 'get_absolute_url'):
            url = target.get_absolute_url()
        else:
            url = '/'
        return HttpResponseRedirect(url)

comment_preview = CommentFormPreview(CommentForm)


def comment(request, bits, context):
    if len(bits) != 1 or bits[0] != 'add':
        from django.http import Http404
        raise Http404
    return comment_preview(request)


def register_custom_urls():
    """register all custom urls"""
    dispatcher.register('comment',  comment)


"""
TODO:
CommentFormPreview pri registrovanem uzivateli jej prihlasi a nezobrazi jeho heslo
CommentFormPreview zobrazi captchu
"""


