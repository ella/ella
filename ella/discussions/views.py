from django import http, newforms as forms
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

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
                'page/category/%s/discussions/%s/ask.html' % (category.path, topic.slug,),
                'page/category/%s/discussions/ask.html' % (category.path,),
                'page/discussions/ask.html',
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

    if (len(bits) >= 2) and (bits[1] == slugify(ugettext('comments'))):
        from ella.comments.urls import comments_custom_urls
        return  comments_custom_urls(request, bits[2:], context)

    if len(bits) != 1:
        raise http.Http404


    return render_to_response(
            (
                'page/category/%s/discussions/%s/question.html' % (category.path, topic.slug,),
                'page/category/%s/discussions/question.html' % (category.path,),
                'page/discussions/question.html',
),
            context,
            context_instance=RequestContext(request)
)
