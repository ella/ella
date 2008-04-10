import logging
from time import strftime
from django import http, newforms as forms
from django.template import RequestContext, loader
from django.shortcuts import render_to_response
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import authenticate, login, logout, get_user
from django.views.generic.list_detail import object_list

from ella.discussions.models import *
from ella.comments.models import Comment
from ella.core.cache.utils import get_cached_object_or_404


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


class LoginForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(required=True, widget=forms.PasswordInput)


def get_ip(request):
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        return request.META['HTTP_X_FORWARDED_FOR']
    return request.META['REMOTE_ADDR']


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
    else:
        if request.POST:
            frm = QuestionForm(request.POST)
            if not frm.is_valid():
                context['question_form_state'] = STATE_INVALID
            context['question_form_state'] = STATE_OK
            if frm.is_valid():
                ctThread = ContentType.objects.get(
                    app_label='discussions',
                    model='TopicThread'
)
                content = frm.cleaned_data['content']
                content = filter_banned_strings(content)
                comment_set = get_comments_on_thread(thr).order_by('submit_date')
                parent = None
                if comment_set.count() > 0:
                    parent = comment_set[0]
                usr = get_user(request)
                cmt = Comment(
                    content=content,
                    subject='',
                    ip_address=get_ip(request),
                    target_ct=ctThread,
                    target_id=thr.id,
                    parent=parent,
                    user=usr,
)
                cmt.save()
    comment_set = get_comments_on_thread(thr).order_by('submit_date')
    context['thread'] = thr
    context['posts'] = comment_set
    context['login_form'] = frmLogin
    context['question_form'] = frm
    context['question_form_action'] = request.get_full_path() #request.build_absolute_uri()
    context['login_form_action'] = '%slogin/' % request.get_full_path()
    context['logout_form_action'] = '%slogout/' % request.get_full_path()
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


def ask_question(request, bits, context):
    if bits:
        raise http.Http404

    topic = context['object']

    form = QuestionForm(request.POST or None)
    if form.is_valid():
        ip = get_ip(request)
        q = Question(**form.cleaned_data)
        q.topic = topic
        q.ip_address = ip

        slug = slugify(form.cleaned_data['title'])
        if Question.objects.filter(topic=topic, slug=slug).count() != 0:
            suffix = 1
            while Question.objects.filter(topic=topic, slug=(slug + str(suffix))).count() != 0:
                suffix += 1
            slug = slug + str(suffx)
        q.slug = slug

        q.save()

        return http.HttpResponseRedirect(q.get_absolute_url())

    context['form'] = form
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
