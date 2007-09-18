from datetime import datetime, timedelta

from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse
from django import newforms as forms
from django.views.decorators.http import require_POST
from django.db import transaction, connection
from django.contrib.contenttypes.models import ContentType
from django.template import RequestContext
from django.conf import settings
from django.contrib.sites.models import Site

from ella.core.cache import get_cached_object_or_404
from ella.core.wizard import Wizard
from ella.polls.models import Poll, Contest, Contestant, Quiz, Result, Choice, Vote

# POLLS specific settings
POLLS_COOKIE_NAME = getattr(settings, 'POLLS_COOKIE_NAME', 'polls_voted')
POLLS_JUST_VOTED_COOKIE_NAME = getattr(settings, 'POLLS_JUST_VOTED_COOKIE_NAME', 'polls_just_voted_voted')
POLLS_MAX_COOKIE_LENGTH = getattr(settings, 'POLLS_MAX_COOKIE_LENGTH', 20)
POLLS_MAX_COOKIE_AGE = getattr(settings, 'POLLS_MAX_COOKIE_AGE', 604800)

POLL_USER_NOT_YET_VOTED = 0
POLL_USER_JUST_VOTED = 1
POLL_USER_ALLREADY_VOTED = 2

CURRENT_SITE = Site.objects.get_current()

def check_vote(request, poll):
    sess_jv = request.session.get(POLLS_JUST_VOTED_COOKIE_NAME, [])
    if poll.id in sess_jv:
        del request.session[POLLS_JUST_VOTED_COOKIE_NAME]
        # TODO - del just my poll, not the entire list !
        return POLL_USER_JUST_VOTED
    # authenticated user - check session
    if request.user.is_authenticated():
        sess = request.session.get(POLLS_COOKIE_NAME, [])
        if poll.id in sess:
            return POLL_USER_ALLREADY_VOTED
        if Vote.objects.filter(poll=poll, user=request.user).count() > 0:
            return POLL_USER_ALLREADY_VOTED
        return POLL_USER_NOT_YET_VOTED
    # anonymous - check cookie
    else:
        cook = request.COOKIES.get(POLLS_COOKIE_NAME, '').split(',')
        if str(poll.id) in cook:
            return POLL_USER_ALLREADY_VOTED
        #if Vote.objects.filter(poll=poll, ip_address=request.META['REMOTE_ADDR']).count() > 0:
        #    return POLL_USER_ALLREADY_VOTED
        return POLL_USER_NOT_YET_VOTED

@require_POST
@transaction.commit_on_success
def poll_vote(request, poll_id):
    """
    Add vote for a poll

    Redirect to object's get_absolute_url() on success.

    Params:
        poll_id: Poll object identifier

    Raises:
        Http404 if no content_type or model is associated with the given IDs
    """
    poll_ct = ContentType.objects.get_for_model(Poll)
    poll = get_cached_object_or_404(poll_ct, pk=poll_id)

    url = get_next_url(request)

    form = QuestionForm(poll.question)(request.POST)
    if form.is_valid():

        # choice data from form
        choice = form.cleaned_data['choice']

        if check_vote(request, poll) != POLL_USER_NOT_YET_VOTED:
            return HttpResponseRedirect(url)

        # update anti-spam - vote saving
        kwa = {}
        if request.user.is_authenticated():
            kwa['user'] = request.user
        if request.META.has_key('REMOTE_ADDR'):
            kwa['ip_address'] = request.META['REMOTE_ADDR']
        vote = Vote(poll=poll, **kwa)
        vote.save()
        # increment votes at choice object
        if vote.id:
            choice.add_vote()

        # update anti-spam - cook, sess
        sess_jv = request.session.get(POLLS_JUST_VOTED_COOKIE_NAME, [])
        sess_jv.append(poll.id)
        request.session[POLLS_JUST_VOTED_COOKIE_NAME] = sess_jv
        response = HttpResponseRedirect(url)
        if request.user.is_authenticated():
            sess = request.session.get(POLLS_COOKIE_NAME, [])
            sess.append(poll.id)
            request.session[POLLS_COOKIE_NAME] = sess
        else:
            cook = request.COOKIES.get(POLLS_COOKIE_NAME, '').split(',')
            if len(cook) > POLLS_MAX_COOKIE_LENGTH:
                cook = cook[1:]
            cook.append(str(poll.id))
            expires = datetime.strftime(datetime.utcnow() + timedelta(seconds=POLLS_MAX_COOKIE_AGE), "%a, %d-%b-%Y %H:%M:%S GMT")
            response.set_cookie(
                POLLS_COOKIE_NAME,
                value=','.join(cook),
                max_age=POLLS_MAX_COOKIE_AGE,
                expires=expires,
                path='/',
                domain=CURRENT_SITE.domain,
                secure=None
)

        return response

    return render_to_response('polls/poll_form.html', {'form' : form, 'next' : url}, context_instance=RequestContext(request))

@transaction.commit_on_success
def contest_vote(request, contest_id):
    # get current contest object
    contest = get_cached_object_or_404(Contest, pk=contest_id)
    forms = []
    forms_are_valid = True
    # questions forms
    for question in contest.questions:
        form = QuestionForm(question)(request.POST or None, prefix=str(question.id))
        if not form.is_valid():
            forms_are_valid = False
        forms.append((question, form))
    # contestant form
    initial = {}
    if request.user.is_authenticated():
        initial['name'] = request.user.first_name
        initial['surname'] = request.user.last_name
        initial['email'] = request.user.email
    contestant_form = ContestantForm(request.POST or None, initial=initial)
    if not contestant_form.is_valid():
        forms_are_valid = False
    # saving contestant
    if forms_are_valid:
        return contest_finish(request, contest, forms)
    return render_to_response((
                'page/category/%s/polls/contest_form.html' % self.contest.category.path,
                'page/polls/contest_form.html',
), {
                'object' : contest,
                'forms' : forms,
                'contestant_form' : contestant_form
},
            context_instance=RequestContext(request)
)

def get_next_url(request):
    """
    Return URL for redirection on success

    Try to get it from:
        * POST param 'next'
        * HTTP_REFERER
    """
    if 'next' in request.POST and request.POST['next'].startswith('/'):
        return request.POST['next']
    else:
        return request.META.get('HTTP_REFERER', '/')

class MyRadioSelect(forms.RadioSelect):
    def render(self, name, value, attrs=None, choices=()):
        return self.get_renderer(name, value, attrs, choices)

def QuestionForm(question):
    if  question.allow_multiple:
        choice_field = forms.ModelMultipleChoiceField(
                queryset=question.choices,
                widget=forms.CheckboxSelectMultiple
)
    else:
        choice_field = forms.ModelChoiceField(
                queryset=question.choices,
                widget=MyRadioSelect,
                empty_label=None
)

    class _QuestionForm(forms.Form):
        """
        Question form with all its choices
        """
        choice = choice_field
        def choices(self):
            field = self['choice']
            for choice, input in  zip(field.field.queryset, field.as_widget(field.field.widget)):
                yield (choice, input)

    return _QuestionForm


class ContestantForm(forms.Form):
    """
    Contestant form
    """
    # FIXME - all is required
    name = Contestant._meta.get_field('name').formfield()
    surname = Contestant._meta.get_field('surname').formfield()
    email = Contestant._meta.get_field('email').formfield()
    phonenumber = Contestant._meta.get_field('phonenumber').formfield()
    address = Contestant._meta.get_field('address').formfield()

    def clean(self):
        # TODO - antispam
        return self.cleaned_data

class ContestWizard(Wizard):
    def __init__(self, contest):
        self.contest = contest
        form_list = [ QuestionForm(q) for q in contest.questions ]
        form_list.append(ContestantForm)
        self.extra_context = {'object' : contest, 'question' : self.contest.questions[0]}
        super(ContestWizard, self).__init__(form_list)

    def get_template(self):
        if (self.step + 1) < len(self.form_list):
            return (
                    'page/category/%s/polls/contest_step.html' % self.contest.category.path,
                    'page/polls/contest_step.html',
)
        return (
                'page/category/%s/polls/contestant_form.html' % self.contest.category.path,
                'page/polls/contestant_form.html',
)

    def process_step(self, request, form, step):
        if (step + 1) < len(self.form_list):
            self.extra_context['question'] = self.contest.questions[step]

    @transaction.commit_on_success
    def done(self, request, form_list):
        return contest_finish(request, self.contest, form_list[:-1], form_list[-1])

def contest_finish(request, context, qforms, contestant_form):
    choices = '|'.join(
            '%d:%s' % (
                    question.id,
                    question.allow_multiple and ','.join(c.id for c in f.cleaned_data['choice']) or f.cleaned_data['choice'].id)
                for question, f in zip(contest.questions, qforms)
)
    c = Contestant(
            contest=contest,
            choices=choices,
            **contestant_form.cleaned_data
)
    if request.user:
        c.user = request.user
    c.save()
    return HttpResponseRedirect(get_next_url(request))


class QuizWizard(Wizard):
    def __init__(self, quiz):
        form_list = [ QuestionForm(q) for q in quiz.questions ]
        self.quiz = quiz
        self.extra_context = {'object' : quiz, 'question' : self.quiz.questions[0]}
        super(QuizWizard, self).__init__(form_list)

    def get_template(self):
        return (
                'page/category/%s/polls/quiz_step.html' % self.quiz.category.path,
                'page/polls/quiz_step.html',
)

    def process_step(self, request, form, step):
        if (step + 1) < len(self.form_list):
            self.extra_context['question'] = self.quiz.questions[step+1]

    def done(self, request, form_list):
        points = 0
        questions = []
        for question, f in zip(self.quiz.questions, form_list):
            choices = question.choices[:]
            if question.allow_multiple:
                points += sum(c.points for c in f.cleaned_data['choice'])
                for ch in choices:
                    if ch in f.cleaned_data['choice']:
                        ch.chosen = True
            else:
                points += f.cleaned_data['choice'].points
                for ch in choices:
                    if ch == f.cleaned_data['choice']:
                        ch.chosen = True
                        break
            questions.append((question, choices))

        result = self.quiz.get_result(points)
        result.count += 1
        result.save()
        self.extra_context.update(
                {
                    'result' : result,
                    'points' : points,
                    'questions' : questions
}
)
        return render_to_response(
                (
                    'page/category/%s/polls/quiz_result.html' % self.quiz.category.path,
                    'page/polls/quiz_result.html',
),
                self.extra_context,
                context_instance=RequestContext(request)
)

