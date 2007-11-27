from django import http, newforms as forms
from django.template import RequestContext, loader
from django.shortcuts import render_to_response
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.views.generic.list_detail import object_list

from ella.discussions.models import Question, Topic
from ella.core.cache.utils import get_cached_object_or_404

class QuestionForm(forms.Form):
    title = Question._meta.get_field('title').formfield()
    nickname = Question._meta.get_field('nickname').formfield()
    email = Question._meta.get_field('email').formfield()
    description = Question._meta.get_field('description').formfield()

def ask_question(request, bits, context):
    if bits:
        raise http.Http404

    topic = context['object']

    form = QuestionForm(request.POST or None)
    if form.is_valid():
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            ip = request.META['HTTP_X_FORWARDED_FOR']
        else:
            ip = request.META['REMOTE_ADDR']
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
    top = context['object']
    cat = context['category']
    slug = top.slug
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
            queryset=top.question_set.all(),
            extra_context=context,
            paginate_by=10,
            template_name=loader.select_template(t_list).name,
            **kwargs
)


