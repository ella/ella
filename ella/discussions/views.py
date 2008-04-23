import logging
from time import strftime
import smtplib
from django import http, newforms as forms
from django.core.urlresolvers import reverse
from django.template import RequestContext, loader
from django.shortcuts import render_to_response
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import authenticate, login, logout, get_user
from django.views.generic.list_detail import object_list
from django.contrib.formtools.preview import FormPreview

from ella.discussions.models import *
from ella.comments.models import Comment
from ella.core.cache.utils import get_cached_object_or_404
from ella.core.models import HitCount
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

def get_category_topics_url(category):
    # category.slug/year/_(topics)
    return '/%s/%s/%s/' % (category.slug, strftime('%Y'), slugify(_('topics')))

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

def posts(request, bits, context):
    # TODO !!! REFACTOR !!!
    """ Posts view (list of posts associated to given topic) """
    if not bits:
        return http.Http404('Unsupported url. Slug of topic-thread needed.')
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
        # receiving new post to thread in QuestionForm
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
            HitCount.objects.hit(thr) # increment view counter
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
    context['login_frmThread_state'] = STATE_UNAUTHORIZED
    frmLogin = LoginForm()
    frmLogin = LoginForm(request.POST or None)
    if frmLogin.is_valid():
        state = process_login(request, frmLogin.cleaned_data)
        if state == STATE_OK:
            url = '%s%s' % (topic.get_absolute_url(), slugify(_('create thread')))
            return http.HttpResponseRedirect(url)
        context['login_frmThread_state'] = state

    if frmThread.is_valid():
        data = frmThread.cleaned_data
        thr = TopicThread(
            title=data['title'],
            slug=slugify(data['title']),
            created=datetime.now(),
            author=get_user(request),
            topic=topic
)
        thr.save()
        add_post(data['content'], thr, get_user(request), get_ip(request))
    context['login_frmThread'] = frmLogin
    context['login_frmThread_action'] = '%slogin/' % request.get_full_path()
    context['logout_frmThread_action'] = '%slogout/' % request.get_full_path()
    context['question_frmThread'] = frmThread
    context['question_frmThread_action'] = request.get_full_path()
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

    return object_list(
            request,
            queryset=top.topicthread_set.all(),
            extra_context=context,
            paginate_by=10,
            template_name=loader.select_template(t_list).name,
            **kwargs
)

log = logging.getLogger('ella.discussions')
