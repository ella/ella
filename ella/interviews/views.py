from django.http import Http404, HttpResponseRedirect
from django import forms
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.contrib.formtools.preview import FormPreview
from django.core.paginator import QuerySetPaginator

from ella.core.views import get_templates_from_placement
from ella.interviews.models import Question, Answer
from ella.utils.paginator import paginate_qset, get_page_no
from ella.interviews.conf import interviews_settings

def detail(request, context):
    """ Custom object detail function that adds a QuestionForm to the context. """
    interview = context['object']
    page_no = get_page_no(request)
    qset = interview.get_questions()
    paginator = QuerySetPaginator(qset, interviews_settings.PAGINATION_PER_PAGE)

    if page_no > paginator.num_pages or page_no < 1:
        raise Http404

    page = paginator.page(page_no)

    interviewees = interview.get_interviewees(request.user)
    context.update({
        'interviewees': interviewees,
        'is_paginated': paginator.num_pages > 1,
        'results_per_page': interviews_settings.PAGINATION_PER_PAGE,
        'page': page,
        'form' : QuestionForm(request),
        'questions' : page.object_list,
    })

    return render_to_response(
        get_templates_from_placement('object.html', context['placement']),
        context,
        context_instance=RequestContext(request)
    )

def unanswered(request, context):
    """ Display unanswered questions via rendering page/content_type/interviews.interview/unanswered.html template. """
    interview = context['object']
    interviewees = interview.get_interviewees(request.user)
    context['interviewees'] = interviewees
    context['form'] = QuestionForm(request)
    # result pagination
    qset = interview.unanswered_questions()
    context.update(paginate_qset(request, qset))
    return render_to_response(
        get_templates_from_placement('unanswered.html', context['placement']),
        context,
        context_instance=RequestContext(request)
    )

def list_questions(request, context):
    """
    Displays a list of questions (via rendering
    page/content_type/interviews.interview/reply.html template).
    """
    interview = context['object']

    interviewees = interview.get_interviewees(request.user)
    context['interviewees'] = interviewees

    if not interviewees:
        # no permission
        raise Http404

    # list of all questions
    qset = interview.question_set.all()
    context.update(paginate_qset(request, qset))
    return render_to_response(
        get_templates_from_placement('reply.html', context['placement']),
        context,
        context_instance=RequestContext(request)
    )

def reply(request, context, question_id):
    """

    Can be also called as reply/PK/ which will then display a ReplyForm for the given question.

    Raises Http404 on any error or missing permissions.
    """
    interview = context['object']

    interviewees = interview.get_interviewees(request.user)
    context['interviewees'] = interviewees

    if not interviewees:
        # no permission
        raise Http404

    # no point in caching individual questions
    question = get_object_or_404(
            Question,
            pk=question_id,
            interview=interview
        )

    if request.method.upper() == 'POST':
        form = ReplyForm(interview, interviewees, question, request, request.POST)
        if form.is_valid():
            form.save()
            # go back to the question list
            return HttpResponseRedirect('..')
        else:
            # stay on form
            pass
    else:
        form = ReplyForm(interview, interviewees, question, request)

    context['form'] = form
    context['question'] = question

    return render_to_response(
        get_templates_from_placement('answer_form.html', context['placement']),
        context,
        context_instance=RequestContext(request)
    )

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

        ip = self.request.META['REMOTE_ADDR']

        a = Answer(
                question=self.question,
                interviewee_id=interviewee,
                content=self.cleaned_data['content'],
            )
        a.save()
        return a

class QuestionForm(forms.Form):
    """ Ask a question. If current user is authenticated, don't ask him for nick/email. """
    nickname = Question._meta.get_field('nickname').formfield(required=True)
    email = Question._meta.get_field('email').formfield()
    content = Question._meta.get_field('content').formfield()

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(QuestionForm, self).__init__(*args, **kwargs)

        # if a user is logged in, do not ask for nick and/or email
        if self.request.user.is_authenticated():
            del self.fields['nickname']
            del self.fields['email']

class QuestionFormFactory(object):
    def __init__(self, request):
        self.request = request

    def __call__(self, *args, **kwargs):
        return QuestionForm(self.request, *args, **kwargs)

    def __getattr__(self, attname):
        return getattr(QuestionForm, attname)

class QuestionDescriptor(object):
    def __get__(self, qfp, obj_type=None):
        return QuestionFormFactory(qfp.request)

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

    def parse_params(self, context):
        """ Store the context provided by ella to self.state. """
        if not context['object'].can_ask():
            raise Http404
        self.state.update(context)

    def done(self, request, cleaned_data):
        """ Save the question itself. """

        ip = request.META['REMOTE_ADDR']

        question = Question(interview=self.state['object'], ip_address=ip, **cleaned_data)

        if request.user.is_authenticated():
            question.user = request.user

        question.save()

        return HttpResponseRedirect('..')

