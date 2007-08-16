from django.contrib.formtools.preview import FormPreview

from ella.comments import defaults
from ella.comments.forms import CommentForm
from ella.comments.models import Comment

from django.shortcuts import get_object_or_404
from ella.core.cache import get_cached_object_or_404
from ella.core.custom_urls import dispatcher

from django.contrib.contenttypes.models import ContentType

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

class CommentFormPreview(FormPreview):
    preview_template = 'comments/preview.html'
    form_template = 'comments/form.html'
    def parse_params(self, context={}):
        self.context = context
    def done(self, request, cleaned_data):
        CommentForm(request.POST).save(
                other_values={'ip_address': request.META['REMOTE_ADDR']})
        # TODO: get_cached_object_or_404
        ct = get_object_or_404(ContentType, pk=cleaned_data['target_ct'].id)
        target = get_object_or_404(ct.model_class(), pk=cleaned_data['target_id'])
        if hasattr(target, 'get_absolute_url'):
            url = target.get_absolute_url()
        else:
            url = '/'
        return HttpResponseRedirect(url)

comment_preview = CommentFormPreview(CommentForm)

def new_comment(request, object):
    """new comment"""
    return render_to_response('comments/new.html', {'object': object,})

def reply_comment(request, object, target_ct, parent):
    """
    create form with parent binding
    TODO: this should be feasible via get_comment_form
    """
    comment_ct = ContentType.objects.get_for_model(Comment)
    comment_parent = get_cached_object_or_404(comment_ct, pk=parent)

    init_props = {
            'target': '%d:%d' % (target_ct.id, object.id),
            'parent': comment_parent.id,
}
    form = CommentForm(init_props=init_props)
    return render_to_response('comments/reply.html', {'object': object, 'form': form})



def comment(request, bits, context):
    if len(bits) == 1:
        if bits[0] == 'add':
            return comment_preview(request)
        elif bits[0] == 'new':
            return new_comment(request, context['object'])
    if len(bits) == 2:
        try:
            parent_id = int(bits[1])
        except ValueError:
            parent_id = None
        if bits[0] == 'add':
            return reply_comment(request, context['object'], context['ct'], parent_id)
#            return new_comment(request, context['object'])

    from django.http import Http404
    raise Http404


def register_custom_urls():
    """register all custom urls"""
    dispatcher.register('comment',  comment)


"""
TODO:
CommentFormPreview pri registrovanem uzivateli jej prihlasi a nezobrazi jeho heslo
CommentFormPreview zobrazi captchu
"""


