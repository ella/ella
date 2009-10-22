from django.http import Http404, HttpResponse
import logging
from datetime import datetime
from django import http
from django.template import RequestContext, Context
from django.shortcuts import render_to_response
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user
from django.contrib.auth.models import User, AnonymousUser
from django.core.paginator import QuerySetPaginator
from django.conf import settings

from ella.discussions.models import BannedString, Topic, TopicThread, \
    PostViewed, DuplicationError, get_comments_on_thread
from ella.discussions.cache import get_key_comments_on_thread__by_submit_date, get_key_comments_on_thread__spec_filter, comments_on_thread__spec_filter, comments_on_thread__by_submit_date
from ella.oldcomments.models import Comment
from ella.oldcomments.forms import CommentForm
from ella.core.cache.utils import get_cached_object_or_404, delete_cached_object
from ella.oldcomments.defaults import FORM_OPTIONS
from forms import *

DISCUSSIONS_PAGINATE_BY = getattr(settings, 'DISCUSSIONS_PAGINATE_BY', 5)
THREADS_PAGINATE_BY = getattr(settings, 'THREADS_PAGINATE_BY', 5)

def get_ip(request):
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        return request.META['HTTP_X_FORWARDED_FOR']
    return request.META['REMOTE_ADDR']

def add_post(content, thread, user = False, nickname = False, email = '', ip='0.0.0.0', parent = None):
    """
    PARAMS
    content: post content
    thread: TopicThread instance
    ip: IP address
    """
    # invalidate cached thread posts
    delete_cached_object(get_key_comments_on_thread__by_submit_date(None, thread))
    delete_cached_object(get_key_comments_on_thread__spec_filter(None, thread))

    content = filter_banned_strings(content)
    comment_set = get_comments_on_thread(thread).order_by('-parent')
    CT_THREAD = ContentType.objects.get_for_model(TopicThread)

    if comment_set.count() > 0 and not parent:
        parent = comment_set[0]
    elif parent:
        parent = get_cached_object_or_404(Comment, pk = parent)

    if (user):
        cmt = Comment(
            content=content,
            subject='',
            ip_address=ip,
            target_ct=CT_THREAD,
            target_id=thread.id,
            parent=parent,
            user=user,
        )

        cmt.save()

        # post is viewed by its autor
        make_objects_viewed(user, (cmt,))

    elif nickname:
        cmt = Comment(
            content=content,
            subject='',
            ip_address=ip,
            target_ct=CT_THREAD,
            target_id=thread.id,
            parent=parent,
            nickname=nickname,
            email=email,
        )

        cmt.save()

    else:
        raise Exception("Either user or nickname param required!")

def paginate_queryset_for_request(request, qset, paginate_by):
    """ returns appropriate page for view. Page number should
        be set in GET variable 'p', if not set first page is returned.
    """
    item_number_mapping = {}
    for i, c in enumerate(qset):
        item_number_mapping[c._get_pk_val()] = i + 1
    paginator = QuerySetPaginator(qset, paginate_by)
    page_no = request.GET.get('p', paginator.page_range[0])
    try:
        page_no = int(page_no)
        if not page_no in paginator.page_range:
            page_no = paginator.page_range[0]
    except Exception:
        page_no = paginator.page_range[0]
    context = {}
    page = paginator.page(page_no)
    objs = page.object_list
    context['object_list'] = objs
    context.update({
        'is_paginated': paginator.num_pages > 1,
        'results_per_page': paginate_by,
        'page': page,
        'item_number_mapping': item_number_mapping,
    })
    return context

def make_objects_viewed(user, object_list):
    if not isinstance(user, AnonymousUser) and len(object_list)>0:
        CT = ContentType.objects.get_for_model(object_list[0])
        for item in object_list:
            pv = PostViewed.objects.filter(target_ct=CT, target_id=item._get_pk_val(), user=user)
            if pv:
                continue
            post_viewed = PostViewed(target_ct=CT, target_id=item._get_pk_val(), user=user)
            post_viewed.save()

def get_category_topics_url(category):
    return '/%s/%s/%s/' % (category.slug, slugify(_('static')), slugify(_('topics')))

def filter_banned_strings(content):
    REPLACEMENT = '***'
    out = content
    for item in BannedString.objects.values():
        if item['isregexp']:
            out = re.sub(word, REPLACEMENT, out)
            continue
        word = item['expression']
        position = out.find(word)
        while position > -1:
            poslen = len(item['expression']) + position
            out = out[ :position ] + REPLACEMENT + out[ poslen: ]
            position = out.find(word)
    return out

def view_unread(request):
    """ View all posted things since last login. """
    if not isinstance(request.user, User):
        raise http.Http404('User does not exist!')

    u = request.user
    qset = TopicThread.objects.get_unread_topicthreads(request.user)
    context = Context()
    context.update(paginate_queryset_for_request(request, qset, DISCUSSIONS_PAGINATE_BY))
    return render_to_response(
        ('page/content_type/discussions.question/unread_threads.html',),
        context,
        context_instance=RequestContext(request)
    )

def user_posts(request, username):
    """
    View all posts posted by user with username.
    """
    users = User.objects.filter(username=username)
    if not users:
        raise http.Http404('User does not exist!')

    u = users[0]
    CT = ContentType.objects.get_for_model(TopicThread)
    qset = Comment.objects.filter(target_ct=CT).filter(user=u)
    context = Context()
    context.update(paginate_queryset_for_request(request, qset, DISCUSSIONS_PAGINATE_BY))
    return render_to_response(
        ('page/content_type/discussions.question/user_posts.html',),
        context,
        context_instance=RequestContext(request)
    )

def topicthread(request, bits, context):
    """ Posts view (list of posts associated to given topic) """
    if not bits:
        raise http.Http404('Unsupported url. Slug of topic-thread needed.')

    topic = context['object']
    category = context['category']

    thr = TopicThread.objects.get(slug=bits[0])
    user = get_user(request)
    initial = {}

    if user.is_authenticated():
        initial['nickname'] = user.username
        initial['email'] = user.email

    frm = PostForm(initial = initial)

    if request.POST:

        if not settings.DEBUG and not request.is_ajax():
            return Http404, "Accept only AJAX calls."

        frm = PostForm(request.POST)
        if frm.is_valid():
            frm.cleaned_data['content'].strip()

            if user.is_authenticated():
                if frm.cleaned_data['parent']:
                    add_post(frm.cleaned_data['content'], thr, user=user, ip=get_ip(request), parent = frm.cleaned_data['parent'])
                else:
                    add_post(frm.cleaned_data['content'], thr, user=user, ip=get_ip(request))
            else:
                if frm.cleaned_data['parent']:
                    add_post(frm.cleaned_data['content'], thr, nickname=frm.cleaned_data['nickname'], email=frm.cleaned_data['email'], ip=get_ip(request), parent = frm.cleaned_data['parent'])
                else:
                    add_post(frm.cleaned_data['content'], thr, nickname=frm.cleaned_data['nickname'], email=frm.cleaned_data['email'], ip=get_ip(request))
            frm = PostForm() # form reset after succesfull post
            return HttpResponse('', mimetype='text/plain;charset=utf-8')
        else:
            return render_to_response(
                ('common/page/discussions/form.html',),
                {
                    'form': frm,
                    'form_action': thr.get_absolute_url(),
                },
                context_instance=RequestContext(request)
            )

    else:
        thr.hit() # increment view counter

    if request.user.is_staff:
        comment_set = comments_on_thread__by_submit_date(thr) # specialized function created because of caching
    else:
        comment_set = comments_on_thread__spec_filter(thr) # specialized function created because of caching


    context.update(paginate_queryset_for_request(request, comment_set, DISCUSSIONS_PAGINATE_BY)) # adds 'object_list' object list to context
    make_objects_viewed(request.user, context['object_list']) # makes the objects rendered viewed by user
    thread_url = '%s?p=%i' % (thr.get_absolute_url(), int(float(len(comment_set))/DISCUSSIONS_PAGINATE_BY + 0.9999))

    context['topics_url'] = get_category_topics_url(category)
    context['thread'] = thr
    context['add_post_form'] = frm
    context['add_post_form_action'] = thread_url

    tplList = (
        'page/category/%s/content_type/discussions.topicthread/%s/object.html' % (category.path, topic.slug,),
        'page/category/%s/content_type/discussions.topicthread/object.html' % (category.path,),
        'page/content_type/discussions.topicthread/object.html',
    )
    return render_to_response(
        tplList,
        context,
        context_instance=RequestContext(request)
    )


def post_reply(request, context, reply, thread):
    """new reply to a post in the thread"""


    if not settings.DEBUG and not request.is_ajax():
        raise Http404, "Accept only AJAX calls."

    thr = TopicThread.objects.get(slug = thread)
    thread_url = '%s?p=%i' % (thr.get_absolute_url(), int(float(thr.num_posts+1)/DISCUSSIONS_PAGINATE_BY + 0.9999))

    init_props = {}
    init_props['options'] = FORM_OPTIONS['UNAUTHORIZED_ONLY']
    user = get_user(request)
    if user.is_authenticated():
        init_props['nickname'] = user.username
        init_props['email'] = user.email

    if reply:
        parent = get_cached_object_or_404(Comment, pk=reply)
        init_props['target'] = '%d:%d' % (parent.target_ct.id, parent.target.id)
        init_props['parent'] = reply
        context.update ({
                'reply' : True,
               'parent' : parent,
        })
        form = CommentForm(init_props=init_props)
    else:
        ct = ContentType.objects.get_for_model(TopicThread)
        init_props['target'] = '%d:%d' % (ct.id, thr.id)
        form = PostForm(initial=init_props)


    context['form'] = form
    context['form_action'] = thread_url
    return render_to_response(
        ('common/page/discussions/form.html',),
        context,
        context_instance=RequestContext(request)
    )


def create_thread(request, bits, context):
    """ creates new thread (that is new TopicThread and first Comment) """
    topic = context['object']
    frmThread = ThreadForm(request.POST or None)
    user = get_user(request)

    if not settings.DEBUG and not request.is_ajax():
        raise Http404, "Accept only AJAX calls."

    if frmThread.is_valid():
        data = frmThread.cleaned_data
        try:
            if user.is_authenticated():
                thr = TopicThread(
                    title=data['title'],
                    slug=slugify(data['title']),
                    created=datetime.now(),
                    author=get_user(request),
                    topic=topic
                )
                thr.save()
                add_post(data['content'], thr, user=user, ip=get_ip(request))
            else:
                thr = TopicThread(
                    title=data['title'],
                    slug=slugify(data['title']),
                    created=datetime.now(),
                    nickname=data['nickname'],
                    email=data['email'],
                    topic=topic
                )
                thr.save()
                add_post(data['content'], thr, nickname=data['nickname'], email=data['email'], ip=get_ip(request))

            # TODO: invalidate cached thread list

            return http.HttpResponseRedirect(topic.get_absolute_url())
        except DuplicationError:
            context['error'] = _('Thread with given title already exist.')

    category = context['category']
    ct = ContentType.objects.get_for_model(TopicThread)

    context['add_thread_form'] = frmThread
    context['add_thread_form_action'] = request.get_full_path()

    return render_to_response(
            (
                'page/category/%s/content_type/%s.%s/%s/create-thread.html' % (category.path, ct.app_label, ct.model, topic.slug,),
                'page/category/%s/content_type/%s.%s/create-thread.html' % (category.path, ct.app_label, ct.model,),
                'page/content_type/%s.%s/create-thread.html' % (ct.app_label, ct.model,),
            ),
            context,
            context_instance=RequestContext(request)
    )

#def question(request, bits, context):
#    log.debug('question() view')
#    if not bits:
#        raise http.Http404
#
#    topic = context['object']
#    category = context['category']
#    question = get_cached_object_or_404(Question, topic=topic, slug=bits[0])
#    context['topic'] = topic
#    context['object'] = question
#    context['content_type'] = ContentType.objects.get_for_model(Question)
#
#    if len(bits) > 1 and bits[1] == slugify(_('comments')):
#        new_bits = bits[2:]
#    else:
#        new_bits = bits[1:]
#    from ella.oldcomments.urls import comments_custom_urls
#    return comments_custom_urls(request, new_bits, context)

def topic(request, context):
    topic = context['object']  # topic
    category = context['category']
    slug = topic.slug
    log.debug('topic() view')
    # TODO: add caching
    ct = ContentType.objects.get_for_model(Topic)

    context['topics_url'] = get_category_topics_url(category)

    t_list = [
                'page/category/%s/content_type/%s.%s/%s/object.html' % (category.path, ct.app_label, ct.model, slug),
                'page/category/%s/content_type/%s.%s/object.html' % (category.path, ct.app_label, ct.model),
                'page/category/%s/object.html' % (category.path),
                'page/content_type/%s.%s/object.html' % (ct.app_label, ct.model),
                'page/object.html',
            ]

    kwargs = {}
    if 'p' in request.GET:
        kwargs['page'] = request.GET['p']

    qset = topic.topicthread_set.all().order_by('-created')
    context.update(paginate_queryset_for_request(request, qset, THREADS_PAGINATE_BY))

    return render_to_response(
            t_list,
            context,
            context_instance=RequestContext(request)
    )

log = logging.getLogger('ella.discussions')
