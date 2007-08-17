from django.contrib.formtools.preview import FormPreview
from django.contrib.contenttypes.models import ContentType

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import RequestContext

from ella.core.cache import get_cached_object_or_404




class CommentFormPreview(FormPreview):
    """
    TODO:
    CommentFormPreview pri registrovanem uzivateli jej prihlasi a nezobrazi jeho heslo
    CommentFormPreview zobrazi captchu
    """
    preview_template = 'comments/base_preview_template.html'
    form_template = 'comments/base_preview_form_template.html'
    def parse_params(self, context={}):
        self.context = context
    def done(self, request, cleaned_data):
        from ella.comments.forms import CommentForm
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



def new_comment(request, object):
    """new comment"""
    templates = [
        'comments/base_comment_add.html',
    ]
    context = {
        'object': object,
}
    return render_to_response(templates, context, context_instance=RequestContext(request))

def list_comments(request, object):
    templates = [
        'comments/base_comment_list.html',
    ]
    context = {
        'object': object,
}
    return render_to_response(templates, context, context_instance=RequestContext(request))






