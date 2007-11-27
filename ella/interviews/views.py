from django.http import Http404, HttpResponseRedirect
from django import newforms as forms
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.contrib.formtools.preview import FormPreview

from ella.core.custom_urls import dispatcher
from ella.core.middleware import get_current_request
from ella.interviews.models import Interview, Question, Answer

#from django.utils.translation import ugettext
ugettext = lambda x: x
class ReplyForm(forms.Form):
    content = Answer._meta.get_field('content').formfield()

    def __init__(self, interview, interviewees, question, *args, **kwargs):
        self.interview = interview
        self.question = question

        super(ReplyForm, self).__init__(*args, **kwargs)

        if len(interviewees) == 1:
            self.interviewee = interviewees[0]
        else:
            self.fields['interviewee'] = forms.ChoiceField(choices=[ (u'', u'--------') ] + [ (i.pk, unicode(i)) for i in interviewees ])

    def save(self):
        if not self.is_valid():
            raise ValueError, 'Cannot save an invalid form.'

        if hasattr(self, 'interviewee'):
            interviewee = self.interviewee.pk
        else:
            interviewee = self.cleaned_data['interviewee']

        request = get_current_request()
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            ip = request.META['HTTP_X_FORWARDED_FOR']
        else:
            ip = request.META['REMOTE_ADDR']

        a = Answer(
                question=self.question,
                interviewee_id=interviewee,
                content=self.cleaned_data['content'],
)
        a.save()
        return a

def detail(request, context):
    interview = context['object']
    context['form'] = QuestionForm()
    return render_to_response(
            (
                'page/category/%s/content_type/interviews.interview/%s/object.html' % (context['category'].slug, interview.slug),
                'page/category/%s/content_type/interviews.interview/object.html' % context['category'].slug,
                'page/content_type/interviews.interview/object.html',
                'page/object.html',
),
            context,
            context_instance=RequestContext(request)
)

def unanswered(request, bits, context):
    if bits:
        raise Http404

    interview = context['object']
    context['form'] = QuestionForm()
    return render_to_response(
            (
                'page/category/%s/content_type/interviews.interview/%s/unanswered.html' % (context['category'].slug, interview.slug),
                'page/category/%s/content_type/interviews.interview/unanswered.html' % context['category'].slug,
                'page/content_type/interviews.interview/unanswered.html',
),
            context,
            context_instance=RequestContext(request)
)

def reply(request, bits, context):
    interview = context['object']

    if not bits:
        # list of all questions
        return render_to_response(
                (
                    'page/category/%s/content_type/interviews.interview/%s/reply.html' % (context['category'].slug, interview.slug),
                    'page/category/%s/content_type/interviews.interview/reply.html' % context['category'].slug,
                    'page/content_type/interviews.interview/reply.html',
),
                context,
                context_instance=RequestContext(request)
)

    elif len(bits) != 1:
        # some bogus URL
        raise Http404

    interviewees = interview.get_interviewees(request.user)
    if not interviewees:
        # no permission
        raise Http404

    # no point in caching individual questions
    question = get_object_or_404(
            Question,
            pk=bits[0],
            interview=interview
)

    form = ReplyForm(interview, interviewees, question, request.POST or None)
    if form.is_valid():
        form.save()
        # go back to the question list
        return HttpResponseRedirect('..')

    context['form'] = form

    return render_to_response(
            (
                'page/category/%s/content_type/interviews.interview/%s/answer_form.html' % (context['category'].slug, interview.slug),
                'page/category/%s/content_type/interviews.interview/answer_form.html' % context['category'].slug,
                'page/content_type/interviews.interview/answer_form.html',
),
            context,
            context_instance=RequestContext(request)
)

class QuestionForm(forms.Form):
    nickname = Question._meta.get_field('nickname').formfield()
    email = Question._meta.get_field('email').formfield()
    content = Question._meta.get_field('content').formfield()

    def __init__(self, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)

        request = get_current_request()
        # if a user is logged in, do not ask for nick and/or email
        if request.user.is_authenticated():
            del self.fields['nickname']
            del self.fields['email']


class QuestionFormPreview(FormPreview):
    @property
    def preview_template(self):
        interview = self.state['object']
        cat = self.state['category']
        return [
                'page/category/%s/content_type/interviews.interview/%s/ask_preview.html' % (cat.path, interview.slug),
                'page/category/%s/content_type/interviews.interview/ask_preview.html' % cat.path,
                'page/content_type/interviews.interview/ask_preview.html',
            ]

    @property
    def form_template(self):
        interview = self.state['object']
        cat = self.state['category']
        return [
                'page/category/%s/content_type/interviews.interview/%s/ask_form.html' % (cat.path, interview.slug),
                'page/category/%s/content_type/interviews.interview/ask_form.html' % cat.path,
                'page/content_type/interviews.interview/ask_form.html',
            ]

    def parse_params(self, bits, context):
        if not context['object'].can_ask():
            raise Http404
        self.state.update(context)

    def done(self, request, cleaned_data):

        if 'HTTP_X_FORWARDED_FOR' in request.META:
            ip = request.META['HTTP_X_FORWARDED_FOR']
        else:
            ip = request.META['REMOTE_ADDR']

        question = Question(interview=self.state['object'], ip_address=ip, **cleaned_data)

        if request.user.is_authenticated():
            question.user = request.user

        question.save()

        return HttpResponseRedirect('..')

dispatcher.register(slugify(ugettext('unanswered')), unanswered, model=Interview)
dispatcher.register(slugify(ugettext('reply')), reply, model=Interview)
dispatcher.register(slugify(ugettext('ask')), QuestionFormPreview(QuestionForm),  model=Interview)

dispatcher.register_custom_detail(Interview, detail)
