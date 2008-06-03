import logging
from time import strftime
import smtplib
from datetime import datetime
from django import http, newforms as forms
from django.core.urlresolvers import reverse
from django.template import RequestContext, loader, Context
from django.shortcuts import render_to_response
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import authenticate, login, logout, get_user
from django.contrib.auth.models import User, AnonymousUser
from django.views.generic.list_detail import object_list
from django.contrib.formtools.preview import FormPreview
from django.core.paginator import ObjectPaginator
from django.conf import settings

from ella.discussions.models import get_comments_on_thread, Topic, TopicThread, \
BannedString, BannedUser, PostViewed, DuplicationError
from ella.comments.models import Comment
from ella.core.cache.utils import get_cached_object_or_404
import djangoapps.registration.views as reg_views


STATE_UNAUTHORIZED = 'unauthorized'
STATE_EMPTY = 'empty'
STATE_OK = 'ok'
STATE_INVALID = 'invalid'
STATE_NOT_ACTIVE = 'not_active'
STATE_BAD_LOGIN_OR_PASSWORD = 'bad_password'



class QuestionForm(forms.Form):
    """
    title = Question._meta.get_field('title').formfield()
    nickname = Question._meta.get_field('nickname').formfield()
    email = Question._meta.get_field('email').formfield()
    description = Question._meta.get_field('description').formfield()
    """
    content = forms.CharField(required=True, widget=forms.Textarea)

class ThreadForm(QuestionForm):
    title = forms.CharField(required=True)
    content = forms.CharField(required=True, widget=forms.Textarea)

class LoginForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(required=True, widget=forms.PasswordInput)

class RegistrationForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(required=True, widget=forms.PasswordInput)
    password_again = forms.CharField(required=True, widget=forms.PasswordInput)
    email = forms.EmailField()

    def clean_username(self):
        if User.objects.filter(username__exact=self.cleaned_data['username']):
            raise forms.ValidationError(_('Username already exists. Please choose another one.'))
        return self.cleaned_data['username']

    def register_user(self):
        if not(self.is_bound and self.is_valid()):
            return False
        data = self.cleaned_data
        if User.objects.filter(username__exact=data['username']):
            return False
        usr = User.objects.create_user(data['username'], data['email'], data['password'])
        usr.is_staff = False
        usr.save()
        return usr

def get_ip(request):
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        return request.META['HTTP_X_FORWARDED_FOR']
    return request.META['REMOTE_ADDR']

def add_post(content, thread, user, ip='0.0.0.0'):
    """
    PARAMS
    content: post content
    thread: TopicThread instance
    ip: IP address
    """
    content = filter_banned_strings(content)
    comment_set = get_comments_on_thread(thread).order_by('submit_date')
    CT_THREAD = ContentType.objects.get_for_model(TopicThread)
    parent = None
    if comment_set.count() > 0:
        parent = comment_set[0]
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
    CT = ContentType.objects.get_for_model(Comment)
    post_viewed = PostViewed(target_ct=CT, target_id=cmt._get_pk_val(), user=user)
    post_viewed.save()

def paginate_queryset_for_request(request, qset):
    """ returns appropriate page for view. Page number should
        be set in GET variable 'p', if not set first page is returned.
    """
    paginate_by = 5 # default
    if hasattr(settings, 'DISCUSSIONS_PAGINATE_BY'):
        paginate_by = settings.DISCUSSIONS_PAGINATE_BY
    # ugly son of a bitch - adding object property at runtime?!
    for i, c in enumerate(qset):
        ct = ContentType.objects.get_for_model(c)
        setattr(c, 'item_number', i + 1)
        setattr(
            c,
            'get_admin_url',
            reverse('discussions_admin', args=['%s/%s/%d' % (ct.app_label, ct.model, c._get_pk_val())])
)
    paginator = ObjectPaginator(qset, paginate_by)
    page_no = request.GET.get('p', paginator.page_range[0])
    try:
        page_no = int(page_no)
        if not page_no in paginator.page_range:
            page_no = paginator.page_range[0]
    except Exception:
        page_no = paginator.page_range[0]
    context = {}
    objs = paginator.get_page(page_no - 1)
    # make objs viewed by user TODO presunout nasledujici podminku nekam jinam
    if not isinstance(request.user, AnonymousUser):
        CT = ContentType.objects.get_for_model(Comment)
        for item in objs:
            pv = PostViewed.objects.filter(target_ct=CT, target_id=item._get_pk_val())
            if pv:
                continue
            post_viewed = PostViewed(target_ct=CT, target_id=item._get_pk_val(), user=request.user)
            post_viewed.save()
    context['object_list'] = objs
    context.update({
        'is_paginated': paginator.pages > 1,
        'results_per_page': paginate_by,
        'has_next': paginator.has_next_page(page_no - 1),
        'has_previous': paginator.has_previous_page(page_no - 1),
        'page': page_no,
        'next': page_no + 1,
        'previous': page_no - 1,
        'last_on_page': paginator.last_on_page(page_no - 1),
        'first_on_page': paginator.first_on_page(page_no - 1),
        'pages': paginator.pages,
        'hits': paginator.hits,
})
    return context

def get_category_topics_url(category):
    # category.slug/year/_(topics)
    return '/%s/%s/%s/' % (category.slug, slugify(_('static')), slugify(_('topics')))

def process_login(request, login_data):
    usr = authenticate(username=login_data['username'], password=login_data['password'])
    if not usr:
        return STATE_BAD_LOGIN_OR_PASSWORD
    if not usr.is_active:
        return STATE_NOT_ACTIVE
    login(request, usr)
    return STATE_OK #user is logged in

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
    context.update(paginate_queryset_for_request(request, qset))
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
    context.update(paginate_queryset_for_request(request, qset))
    return render_to_response(
        ('page/content_type/discussions.question/user_posts.html',),
        context,
        context_instance=RequestContext(request)
)

def posts(request, bits, context):
    # TODO !!! REFACTOR !!!
    """ Posts view (list of posts associated to given topic) """
    if not bits:
        raise http.Http404('Unsupported url. Slug of topic-thread needed.')
    frm = QuestionForm()
    frmLogin = LoginForm()
    topic = context['object']
    category = context['category']
    # category.slug/year/_(topics)
    context['topics_url'] = get_category_topics_url(category)
    context['question_form_state'] = STATE_EMPTY
    context['login_form_state'] = STATE_UNAUTHORIZED
    thrList = TopicThread.objects.filter(topic=topic)
    thr = TopicThread.objects.get(slug=bits[0])
    if len(bits) > 1:
        if bits[1] == 'login':
            f = LoginForm(request.POST)
            if f.is_valid():
                state = process_login(request, f.cleaned_data)
                if state == STATE_OK:
                    return http.HttpResponseRedirect(thr.get_absolute_url())
                context['login_form_state'] = state
        elif bits[1] == 'logout':
            logout(request)
            return http.HttpResponseRedirect(thr.get_absolute_url())
        elif bits[1] == 'register':
            return http.HttpResponseRedirect(reverse('registration_register'))
    else:
        # receiving new post in QuestionForm
        if request.POST:
            frm = QuestionForm(request.POST)
            if not frm.is_valid():
                context['question_form_state'] = STATE_INVALID
            elif frm.cleaned_data['content'].strip():
                context['question_form_state'] = STATE_OK
                add_post(frm.cleaned_data['content'], thr, get_user(request), get_ip(request))
            else:
                context['question_form_state'] = STATE_INVALID
        else:
            thr.hit() # increment view counter
    if request.user.is_staff:
        comment_set = get_comments_on_thread(thr).order_by('submit_date')
    else:
        comment_set = get_comments_on_thread(thr).filter(is_public__exact=True).order_by('submit_date')
    thread_url = '%s/' % thr.get_absolute_url()
    context['thread'] = thr
    context['posts'] = comment_set
    context['login_form'] = frmLogin
    context['register_form_url'] = '%sregister/' % thread_url
    context['question_form'] = frm
    context['question_form_action'] = thread_url
    context['login_form_action'] = '%slogin/' % thread_url
    context['logout_form_action'] = '%slogout/' % thread_url
    context.update(paginate_queryset_for_request(request, comment_set))
    tplList = (
        'page/category/%s/content_type/discussions.question/%s/posts.html' % (category.path, topic.slug,),
        'page/category/%s/content_type/discussions.question/posts.html' % (category.path,),
        'page/content_type/discussions.question/posts.html',
)
    return render_to_response(
        tplList,
        context,
        context_instance=RequestContext(request)
)

def create_thread(request, bits, context):
    """ creates new thread (that is new TopciThread and first Comment) """
    topic = context['object']
    frmThread = ThreadForm(request.POST or None)
    context['login_form_state'] = STATE_UNAUTHORIZED
    frmLogin = LoginForm(request.POST or None)
    if frmLogin.is_valid():
        state = process_login(request, frmLogin.cleaned_data)
        if state == STATE_OK:
            url = '%s%s' % (topic.get_absolute_url(), slugify(_('create thread')))
            return http.HttpResponseRedirect(url)
        context['login_form_state'] = state

    if frmThread.is_valid():
        data = frmThread.cleaned_data
        thr = TopicThread(
            title=data['title'],
            slug=slugify(data['title']),
            created=datetime.now(),
            author=get_user(request),
            topic=topic
)
        try:
            thr.save()
            add_post(data['content'], thr, get_user(request), get_ip(request))
            return http.HttpResponseRedirect(topic.get_absolute_url())
        except DuplicationError:
            context['error'] = _('Thread with given title already exist.')
    context['login_form'] = frmLogin
    context['login_form_action'] = '%slogin/' % request.get_full_path()
    context['logout_form_action'] = '%slogout/' % request.get_full_path()
    context['question_form'] = frmThread
    context['question_form_action'] = request.get_full_path()
    category = context['category']
    return render_to_response(
            (
                'page/category/%s/content_type/discussions.question/%s/ask.html' % (category.path, topic.slug,),
                'page/category/%s/content_type/discussions.question/ask.html' % (category.path,),
                'page/content_type/discussions.question/ask.html',
),
            context,
            context_instance=RequestContext(request)
)

def question(request, bits, context):
    log.debug('question() view')
    if not bits:
        raise http.Http404

    topic = context['object']
    category = context['category']
    question = get_cached_object_or_404(Question, topic=topic, slug=bits[0])
    context['topic'] = topic
    context['object'] = question
    context['content_type'] = ContentType.objects.get_for_model(Question)

    if len(bits) > 1 and bits[1] == slugify(_('comments')):
        new_bits = bits[2:]
    else:
        new_bits = bits[1:]
    from ella.comments.urls import comments_custom_urls
    return comments_custom_urls(request, new_bits, context)

def topic(request, context):
    top = context['object']  # topic
    cat = context['category']
    context['topics_url'] = get_category_topics_url(cat)
    slug = top.slug
    log.debug('topic() view')
    # TODO: add caching
    ct = ContentType.objects.get_for_model(Topic)
    t_list = [
                'page/category/%s/content_type/%s.%s/%s/object.html' % (cat.path, ct.app_label, ct.model, slug),
                'page/category/%s/content_type/%s.%s/object.html' % (cat.path, ct.app_label, ct.model),
                'page/category/%s/object.html' % (cat.path),
                'page/content_type/%s.%s/object.html' % (ct.app_label, ct.model),
                'page/object.html',
            ]

    kwargs = {}
    if 'p' in request.GET:
        kwargs['page'] = request.GET['p']
    qset = top.topicthread_set.all()
    #context.update(paginate_queryset_for_request(request, qset))
    return object_list(
            request,
            queryset=qset,
            extra_context=context,
            paginate_by=10,
            template_name=loader.select_template(t_list).name,
            **kwargs
)

log = logging.getLogger('ella.discussions')
