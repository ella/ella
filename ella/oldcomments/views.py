import logging

from django.contrib.formtools.preview import FormPreview
from django.contrib.contenttypes.models import ContentType

from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _

from ella.core.cache import get_cached_object_or_404
from ella.core.views import get_templates_from_placement

from ella.oldcomments.models import Comment
from ella.oldcomments.forms import CommentForm
from ella.oldcomments.defaults import FORM_OPTIONS

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
        ip = request.META['REMOTE_ADDR']

        CommentForm(request.POST).save(
                other_values={'ip_address': ip}
            )

        ct = get_cached_object_or_404(ContentType, pk=cleaned_data['target_ct'].id)
        target = get_cached_object_or_404(ct, pk=cleaned_data['target_id'])

        if 'redir' in request.POST:
            url = request.POST['redir']
        elif hasattr(target, 'get_absolute_url'):
            url = target.get_absolute_url()
        else:
            url = '/'
        return HttpResponseRedirect(url)

def new_comment(request, context, reply=None):
    """new comment for specified object"""
    init_props = {
        'target': '%d:%d' % (context['content_type'].id, context['object']._get_pk_val()),
        'options' : FORM_OPTIONS['UNAUTHORIZED_ONLY'],
    }
    if reply:
        init_props['parent'] = reply
        context.update({
                'reply' : True,
                'parent' : get_cached_object_or_404(
                        Comment,
                        pk=reply,
                        target_ct=context['content_type'],
                        target_id=context['object']._get_pk_val()
                    ),
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

