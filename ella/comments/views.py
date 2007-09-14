from django.contrib.formtools.preview import FormPreview
from django.contrib.contenttypes.models import ContentType

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import RequestContext

from ella.core.cache import get_cached_object_or_404
from ella.core.models import Category

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
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            ip = request.META['HTTP_X_FORWARDED_FOR']
        else:
            ip = request.META['REMOTE_ADDR']

        CommentForm(request.POST).save(
                other_values={'ip_address': ip}
)

        ct = get_cached_object_or_404(ContentType, pk=cleaned_data['target_ct'].id)
        target = get_cached_object_or_404(ct, pk=cleaned_data['target_id'])

        if hasattr(target, 'get_absolute_url'):
            url = target.get_absolute_url()
        else:
            url = '/'
        return HttpResponseRedirect(url)



def new_comment(request, object):
    """new comment"""
    cat = get_cached_object_or_404(Category, pk=object.category_id)
    opts = object._meta
    templates = [
        'comments/%s/%s.%s/%s_comment_add.html' % (cat.path, opts.app_label, opts.module_name, object.slug),
        'comments/%s/%s.%s/base_comment_add.html' % (cat.path, opts.app_label, opts.module_name),
        'comments/%s/base_comment_add.html' % cat.path,
        'comments/base_comment_add.html',
    ]
    context = {
        'object': object,
        'category': cat,
}
    return render_to_response(templates, context, context_instance=RequestContext(request))

def list_comments(request, object):
    cat = get_cached_object_or_404(Category, pk=object.category_id)
    opts = object._meta
    templates = [
        'comments/%s/%s.%s/%s_comment_list.html' % (cat.path, opts.app_label, opts.module_name, object.slug),
        'comments/%s/%s.%s/base_comment_list.html' % (cat.path, opts.app_label, opts.module_name),
        'comments/%s/base_comment_list.html' % cat.path,
        'comments/base_comment_list.html',
    ]
    context = {
        'object': object,
        'category': cat,
}
    return render_to_response(templates, context, context_instance=RequestContext(request))


