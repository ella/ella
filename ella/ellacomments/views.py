from ella.ellacomments.models import CommentOptionsObject, BannedIP
import operator

from django.contrib import comments
from django.contrib.comments import signals
from django.contrib.comments.views.comments import CommentPostBadRequest
from django.utils.html import escape
from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, Http404
from django.db.models import Q
from django.db import transaction
from django.core.paginator import Paginator
from django.conf import settings
from django.views.decorators.csrf import csrf_protect

from ella.core.views import get_templates_from_placement

@csrf_protect
@transaction.commit_on_success
def post_comment(request, context, parent_id=None):
    'Mostly copy-pasted from django.contrib.comments.views.comments'
    opts = CommentOptionsObject.objects.get_for_object(context['object'])
    if opts.blocked:
        raise Http404('Comments are blocked for this object.')
    context['opts'] = opts

    parent = None
    if parent_id:
        parent = get_object_or_404(comments.get_model(), pk=parent_id)

    ip_address = request.META.get('REMOTE_ADDR', None)
    try:
        ip_ban = BannedIP.objects.get(ip_address=ip_address)
    except BannedIP.DoesNotExist:
        ip_ban = None

    if request.method != 'POST' or ip_ban:
        initial = {}
        if parent:
            if parent.title.startswith('Re:'):
                initial['title'] = parent.title
            else:
                initial['title'] = u'Re: %s' % parent.title
        form = comments.get_form()(context['object'], parent=parent_id, initial=initial)
        context.update({
                'parent': parent,
                'form': form,
                'ip_ban': ip_ban,
            })
        return render_to_response(
            get_templates_from_placement('comment_form.html', context['placement']),
            context,
            RequestContext(request)
        )

    # Fill out some initial data fields from an authenticated user, if present
    data = request.POST.copy()

    if request.user.is_authenticated():
        if not data.get('name', ''):
            data["name"] = request.user.get_full_name() or request.user.username
        if not data.get('email', ''):
            data["email"] = request.user.email

    # construct the form
    form = comments.get_form()(context['object'], data=data, parent=parent_id)

    # Check security information
    if form.security_errors():
        return CommentPostBadRequest(
            "The comment form failed security verification: %s" % \
                escape(str(form.security_errors())))

    # Do we want to preview the comment?
    preview = "preview" in data

    # Check to see if the POST data overrides the view's next argument.
    next = data.get("next", "%s%s/" % (context['placement'].get_absolute_url(), slugify(_('comments'))))

    # If there are errors or if we requested a preview show the comment
    if form.errors or preview:
        context.update({
                "form" : form,
                'parent': parent,
                "next": next,
            })
        return render_to_response(
            get_templates_from_placement(form.errors and 'comment_form.html' or 'comment_preview.html', context['placement']),
            context,
            RequestContext(request)
        )

    # Otherwise create the comment
    comment = form.get_comment_object()
    comment.ip_address = request.META.get("REMOTE_ADDR", None)
    if request.user.is_authenticated():
        comment.user = request.user

    # Signal that the comment is about to be saved
    responses = signals.comment_will_be_posted.send(
        sender  = comment.__class__,
        comment = comment,
        request = request
    )

    for (receiver, response) in responses:
        if response == False:
            return CommentPostBadRequest(
                "comment_will_be_posted receiver %r killed the comment" % receiver.__name__)

    if opts.premoderated:
        comment.is_public = False

    # Save the comment and signal that it was saved
    comment.save()
    signals.comment_was_posted.send(
        sender  = comment.__class__,
        comment = comment,
        request = request
    )

    return HttpResponseRedirect(next)


def list_comments(request, context):

    # basic queryset
    qs = comments.get_model().objects.for_model(context['object']).order_by('tree_path')

    # XXX factor out into a manager
    qs = qs.filter(is_public=True)
    if getattr(settings, 'COMMENTS_HIDE_REMOVED', False):
        qs = qs.filter(is_removed=False)

    # only individual branches requested
    if 'ids' in request.GET:
        ids = request.GET.getlist('ids')
        # branch is everything whose tree_path begins with the same prefix
        qs = qs.filter(reduce(operator.or_, map(lambda x: Q(tree_path__startswith=x.zfill(10)), ids)))

    # pagination
    if 'p' in request.GET and request.GET['p'].isdigit():
        page_no = int(request.GET['p'])
    else:
        page_no = 1

    paginate_by = getattr(settings, 'COMMENTS_PAGINATE_BY', 50)
    paginator = Paginator(qs, paginate_by)

    if page_no > paginator.num_pages or page_no < 1:
        raise Http404()

    page = paginator.page(page_no)
    context.update({
        'comment_list': page.object_list,
        'page': page,
        'is_paginated': paginator.num_pages > 1,
        'results_per_page': paginate_by,
    })

    return render_to_response(
        get_templates_from_placement('comment_list.html', context['placement']),
        context,
        RequestContext(request)
    )

