from django.http import Http404, HttpResponseRedirect
from django import newforms as forms
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.contrib.formtools.preview import FormPreview
from django.core.paginator import Paginator, QuerySetPaginator
from django.conf import settings

from ella.core.middleware import get_current_request
from ella.core.views import get_templates_from_placement
from ella.interviews.models import Question, Answer


class ReplyForm(forms.Form):
    """ A form representing the reply, it also contains the mechanism needed to actually save the reply. """
    content = Answer._meta.get_field('content').formfield()

    def __init__(self, interview, interviewees, question, request, *args, **kwargs):
        self.interview = interview
        self.question = question
        self.request = request

        super(ReplyForm, self).__init__(*args, **kwargs)

        if len(interviewees) == 1:
            self.interviewee = interviewees[0]
        else:
            from django.utils.translation import ugettext
            self.fields['interviewee'] = forms.ChoiceField(
                    choices=[ (u'', u'--------') ] + [ (i.pk, unicode(i)) for i in interviewees ],
                    label=ugettext('Interviewee')
)

    def save(self):
        if not self.is_valid():
            raise ValueError, 'Cannot save an invalid form.'

        if hasattr(self, 'interviewee'):
            interviewee = self.interviewee.pk
        else:
            interviewee = self.cleaned_data['interviewee']

        if 'HTTP_X_FORWARDED_FOR' in self.request.META:
            ip = self.request.META['HTTP_X_FORWARDED_FOR']
        else:
            ip = self.request.META['REMOTE_ADDR']

        a = Answer(
                question=self.question,
                interviewee_id=interviewee,
                content=self.cleaned_data['content'],
)
        a.save()
        return a

def detail(request, context):
    """ Custom object detail function that adds a QuestionForm to the context. """
    interview = context['object']

    # pagination
    pagination_by = getattr(settings, 'INTERVIEW_PAGINATION_PER_PAGE', 5)

    if 'p' in request.GET and request.GET['p'].isdigit():
        page = int(request.GET['p'])
    else:
        page = 1

    qset = interview.get_questions()
    paginator = QuerySetPaginator(qset, pagination_by)
    page_content = paginator.page(page)

    if page > paginator.num_pages:
        raise Http404

    context.update({
        'is_paginated': paginator.num_pages > 1,
        'results_per_page': pagination_by,
        'has_next': page_content.has_next(),
        'has_previous': page_content.has_previous(),
        'page': page,
        'next': page_content.next_page_number(),
        'previous': page_content.previous_page_number(),
        'last_on_page': page_content.end_index(),
        'first_on_page': page_content.start_index(),
        'pages': paginator.num_pages,
        'hits' : paginator.count,
        'form' : QuestionForm(request=request),
        'questions' : page_content.object_list,
})

    return render_to_response(
        get_templates_from_placement('object.html', context['placement']),
        context,
        context_instance=RequestContext(request)
)

def unanswered(request, bits, context):
    """ Display unanswered questions via rendering page/content_type/interviews.interview/unanswered.html template. """
    if bits:
        # invalid URL
        raise Http404

    interview = context['object']
    context['form'] = QuestionForm(request=request)
    return render_to_response(
        get_templates_from_placement('unanswered.html', context['placement']),
        context,
        context_instance=RequestContext(request)
)

def reply(request, bits, context):
    """
    If called without parameters will display a list of questions
    (via rendering page/content_type/interviews.interview/reply.html template).

    Can be also called as reply/PK/ which will then display a ReplyForm for the given question.

    Raises Http404 on any error or missing permissions.
    """
    interview = context['object']

    interviewees = interview.get_interviewees(request.user)
    if not interviewees:
        # no permission
        raise Http404

    elif not bits:
        # list of all questions
        return render_to_response(
            get_templates_from_placement('reply.html', context['placement']),
            context,
            context_instance=RequestContext(request)
)

    elif len(bits) != 1:
        # some bogus URL
        raise Http404

    # no point in caching individual questions
    question = get_object_or_404(
            Question,
            pk=bits[0],
            interview=interview
)

    form = ReplyForm(interview, interviewees, question, request, request.POST or None)
    if form.is_valid():
        form.save()
        # go back to the question list
        return HttpResponseRedirect('..')

    context['form'] = form
    context['question'] = question

    return render_to_response(
        get_templates_from_placement('answer_form.html', context['placement']),
        context,
        context_instance=RequestContext(request)
)

class QuestionForm(forms.Form):
    """ Ask a question. If current user is authenticated, don't ask him for nick/email. """
    nickname = Question._meta.get_field('nickname').formfield(required=True)
    email = Question._meta.get_field('email').formfield()
    content = Question._meta.get_field('content').formfield()

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super(QuestionForm, self).__init__(*args, **kwargs)

        # if a user is logged in, do not ask for nick and/or email
        if self.request.user.is_authenticated():
            del self.fields['nickname']
            del self.fields['email']

class QuestionDescriptor(object):
    def __get__(self, qfp, obj_type=None):
        qfp.form_class.request = qfp.request
        return qfp.form_class

class QuestionFormPreview(FormPreview):
    """ FormPreview subclass that handles the question asking mechanism. """
    form = QuestionDescriptor()
    def __call__(self, request, *args, **kwargs):
        self.request = request
        return super(QuestionFormPreview, self).__call__(request, *args, **kwargs)

    def __init__(self, form):
        self.form_class = form
        self.state = {}

    @property
    def preview_template(self):
        return get_templates_from_placement('ask_preview.html', self.state['placement'])

    @property
    def form_template(self):
        return get_templates_from_placement('ask_form.html', self.state['placement'])

    def parse_params(self, bits, context):
        """ Store the context provided by ella to self.state. """
        if not context['object'].can_ask() or bits:
            raise Http404
        self.state.update(context)

    def done(self, request, cleaned_data):
        """ Save the question itself. """

        if 'HTTP_X_FORWARDED_FOR' in request.META:
            ip = request.META['HTTP_X_FORWARDED_FOR']
        else:
            ip = request.META['REMOTE_ADDR']

        question = Question(interview=self.state['object'], ip_address=ip, **cleaned_data)

        if request.user.is_authenticated():
            question.user = request.user

        question.save()

        return HttpResponseRedirect('..')

