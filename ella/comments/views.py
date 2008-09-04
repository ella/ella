import logging

from django.contrib.formtools.preview import FormPreview
from django.contrib.contenttypes.models import ContentType

from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _

from ella.core.cache import get_cached_object_or_404
from ella.core.views import get_templates_from_placement

from ella.comments.models import Comment
from ella.comments.forms import CommentForm
from ella.comments.defaults import FORM_OPTIONS

log = logging.getLogger('ella.comments')

class CommentFormPreview(FormPreview):
    """comment form preview with extended template calls"""
    @property
    def preview_template(self):
        return get_templates_from_placement('comments/preview.html', placement=self.state['placement'])

    @property
    def form_template(self):
        return get_templates_from_placement('comments/form.html', placement=self.state['placement'])

    def parse_params(self, context={}):
        self.state.update(context)

    def done(self, request, cleaned_data):
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

def new_comment(request, context, reply=None):
    import pdb;pdb.set_trace()
    """new comment for specified object"""
    init_props = {
        'target': '%d:%d' % (context['content_type'].id, context['object']._get_pk_val()),
        'options' : FORM_OPTIONS['UNAUTHORIZED_ONLY'],
}
    if reply:
        init_props['parent'] = reply
        context.update({
                'reply' : True,
                'parent' : get_cached_object_or_404(Comment, pk=reply, target_ct=context['content_type'], target_id=context['object']._get_pk_val()),
})
    form = CommentForm(init_props=init_props)
    context['form'] = form
    templates = get_templates_from_placement('comments/form.html', context['placement'])
    return render_to_response(templates, context, context_instance=RequestContext(request))

def list_comments(request, context):
    """list comments for specified object"""
    comment_list = Comment.objects.get_list_for_object(context['object'])
    if 'ids' in request.GET:
        ids = set(request.GET.getlist('ids'))
        new_comment_list = []
        for c in comment_list:
            if str(c.id) in ids:
                new_comment_list.append(c)
            elif '/' in c.path and c.path[0:c.path.find('/')] in ids:
                new_comment_list.append(c)
        comment_list = new_comment_list

    context.update({
            'comment_count' : Comment.objects.get_count_for_object(context['object']),
            'comment_list' : comment_list,
})
    templates = get_templates_from_placement('comments/list.html', context['placement'])
    return render_to_response(templates, context, context_instance=RequestContext(request))

def comments_custom_urls(request, bits, context):
    if len(bits) == 2:
        if bits[0] == slugify(_('reply')) and bits[1].isdigit():
            return new_comment(request, context, reply=int(bits[1]))

    if len(bits) == 1:
        if bits[0] == slugify(_('preview')):
            if request.method == 'GET':
                log.warning('Preview should be used only with POST.')
                raise Http404('Preview should be used only with POST.')
            comment_preview = CommentFormPreview(CommentForm)
            return comment_preview(request, context)
        elif bits[0] == slugify(_('new')):
            return new_comment(request, context)

    if len(bits) == 0:
        return list_comments(request, context)

    raise Http404

