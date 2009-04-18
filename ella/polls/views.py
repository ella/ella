from datetime import datetime, timedelta
from itertools import chain
import time

from django.shortcuts import render_to_response
from django.utils.translation import ugettext, ugettext_lazy as _
from django.http import HttpResponseRedirect, Http404
from django import forms
from django.views.decorators.http import require_POST
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from django.template import RequestContext
from django.conf import settings
from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode
from django.utils.html import escape

from ella.core.cache import get_cached_object_or_404
from ella.core.views import get_templates_from_placement
from ella.utils.wizard import Wizard
from ella.polls.models import Poll, Contestant, Vote, ACTIVITY_NOT_YET_ACTIVE, ACTIVITY_ACTIVE, ACTIVITY_CLOSED


# POLLS specific settings
POLLS_COOKIE_NAME = getattr(settings, 'POLLS_COOKIE_NAME', 'polls_voted')
POLLS_JUST_VOTED_COOKIE_NAME = getattr(settings, 'POLLS_JUST_VOTED_COOKIE_NAME', 'polls_just_voted_voted')
POLLS_NO_CHOICE_COOKIE_NAME = getattr(settings, 'POLLS_NO_CHOICE_COOKIE_NAME', 'polls_no_choice')
POLLS_MAX_COOKIE_LENGTH = getattr(settings, 'POLLS_MAX_COOKIE_LENGTH', 20)
POLLS_MAX_COOKIE_AGE = getattr(settings, 'POLLS_MAX_COOKIE_AGE', 604800)
POLLS_IP_VOTE_TRESHOLD = 10 * 60

POLL_USER_NOT_YET_VOTED = 0
POLL_USER_JUST_VOTED = 1
POLL_USER_ALLREADY_VOTED = 2
POLL_USER_NO_CHOICE = 3


def check_vote(request, poll):
    """
    To avoid multiple poll votes of the same user.

    Uses sessions (authenticatedd users) or cookies (annonymous users) at first.
    Then it looks it up in Votes.

    Return choices:
     * User not yet voted
     * User just voted
     * User allready voted
     * User try to vote with no choice (usefull to display a message in a Poll box)
    """
    sess_jv = request.session.get(POLLS_JUST_VOTED_COOKIE_NAME, [])
    # removing just voted info from session
    if poll.id in sess_jv:
        del request.session[POLLS_JUST_VOTED_COOKIE_NAME]
        # TODO - del just my poll, not the entire list !
        return POLL_USER_JUST_VOTED
    # removing no vote info from session
    sess_nv = request.session.get(POLLS_NO_CHOICE_COOKIE_NAME, [])
    if poll.id in sess_nv:
        del request.session[POLLS_NO_CHOICE_COOKIE_NAME]
        # TODO - del just my poll, not the entire list !
        return POLL_USER_NO_CHOICE
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
        treshold = datetime.fromtimestamp(time.time() - POLLS_IP_VOTE_TRESHOLD)
        if request.META.has_key('HTTP_X_FORWARDED_FOR'):
            ip_addr = request.META['HTTP_X_FORWARDED_FOR']
        else:
            ip_addr = request.META['REMOTE_ADDR']
        voteCount = Vote.objects.filter(poll=poll, ip_address=ip_addr, time__gte=treshold).count()
        if voteCount > 0:
            return POLL_USER_ALLREADY_VOTED
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

        # poll must be active
        if not poll.is_active():
            return HttpResponseRedirect(url)

        # choice data from form
        choice = form.cleaned_data['choice']

        if check_vote(request, poll) != POLL_USER_NOT_YET_VOTED:
            return HttpResponseRedirect(url)

        # update anti-spam - vote saving
        kwa = {}
        if request.user.is_authenticated():
            kwa['user'] = request.user
        if request.META.has_key('HTTP_X_FORWARDED_FOR'):
            kwa['ip_address'] = request.META['HTTP_X_FORWARDED_FOR']
        else:
            kwa['ip_address'] = request.META['REMOTE_ADDR']
        vote = Vote(poll=poll, **kwa)
        vote.save()
        # increment votes at choice object
        if vote.id and choice != None:
            if type(choice) == list:
                for c in choice:
                    c.add_vote()
            else:
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
                domain=Site.objects.get_current().domain,
                secure=None
            )

        return response

    # no choice
    # FIXME how to catch specific error? try to catch validationError exc?
    if form['choice'].errors:
        sess_nv = request.session.get(POLLS_NO_CHOICE_COOKIE_NAME, [])
        sess_nv.append(poll.id)
        request.session[POLLS_NO_CHOICE_COOKIE_NAME] = sess_nv
        return HttpResponseRedirect(url)

    # we are not here never (for now)
    return response

@transaction.commit_on_success
def contest_vote(request, context):

    contest = context['object']

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
    if forms_are_valid and contest.is_active():
        return contest_finish(request, context, forms, contestant_form)
    context.update({
            'forms' : forms,
            'contestant_form' : contestant_form,
            'activity_not_yet_active' : ACTIVITY_NOT_YET_ACTIVE,
            'activity_active' : ACTIVITY_ACTIVE,
            'activity_closed' : ACTIVITY_CLOSED
        })
    return render_to_response(
        get_templates_from_placement('form.html', context['placement']),
        context,
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

class MyCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        str_values = set([force_unicode(v) for v in value]) # Normalize to strings.
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
            cb = forms.CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            option_value = force_unicode(option_value)
            yield mark_safe(u'<label>%s %s</label>' % (cb.render(name, option_value), escape(force_unicode(option_label))))


class MyRadioSelect(forms.RadioSelect):
    def render(self, name, value, attrs=None, choices=()):
        return self.get_renderer(name, value, attrs, choices)

def QuestionForm(question):
    if  question.allow_multiple:
        choice_field = forms.ModelMultipleChoiceField(
                queryset=question.choices,
                widget=MyCheckboxSelectMultiple,
                required = not question.allow_no_choice
        )
    else:
        choice_field = forms.ModelChoiceField(
                queryset=question.choices,
                widget=MyRadioSelect,
                empty_label=None,
                required = not question.allow_no_choice
        )

    class _QuestionForm(forms.Form):
        """
        Question form with all its choices
        """
        choice = choice_field
        def choices(self):
            field = self['choice']
            # TODO: move choice percentage to question and use it here!!
            for choice, input in  zip(field.field.queryset, field.as_widget(field.field.widget)):
                yield (choice, input)

    return _QuestionForm


class ContestantForm(forms.Form):
    name = Contestant._meta.get_field('name').formfield()
    surname = Contestant._meta.get_field('surname').formfield()
    email = Contestant._meta.get_field('email').formfield()
    phonenumber = Contestant._meta.get_field('phonenumber').formfield()
    address = Contestant._meta.get_field('address').formfield()
    count_guess = Contestant._meta.get_field('count_guess').formfield()
    #accept_conditions = forms.BooleanField()

    def clean(self):
        # TODO - antispam
        return self.cleaned_data

@transaction.commit_on_success
def contest_finish(request, context, qforms, contestant_form):
    contest = context['object']
    email = contestant_form.cleaned_data['email']
    if Contestant.objects.filter(email=email, contest=contest).count() > 0:
        context.update({
                'duplicate' : True,
                'forms' : qforms,
                'contestant_form' : contestant_form,
            })
        return render_to_response(
            get_templates_from_placement('form.html', context['placement']),
            context,
            context_instance=RequestContext(request)
        )

    choices = '|'.join(
            '%d:%s' % (
                    question.id,
                    question.allow_multiple and ','.join(str(c.id) for c in sorted(f.cleaned_data['choice'], key=lambda ch: ch.id)) or f.cleaned_data['choice'].id)
                for question, f in sorted(qforms,key=lambda q: q[0].id)
        )
    c = Contestant(
            contest=contest,
            choices=choices,
            **contestant_form.cleaned_data
        )
    if request.user.is_authenticated():
        c.user = request.user
    c.save()
    return HttpResponseRedirect(contest.get_absolute_url() +slugify(ugettext('result')) + u'/')

def contest_result(request, bits, context):
    if bits:
        raise Http404

    return render_to_response(
        get_templates_from_placement('result.html', context['placement']),
        context,
        context_instance=RequestContext(request)
    )

def contest_conditions(request, bits, context):
    if bits:
        raise Http404

    return render_to_response(
        get_templates_from_placement('conditions.html', context['placement']),
        context,
        context_instance=RequestContext(request)
    )

class ContestWizard(Wizard):
    def __init__(self, contest):
        self.contest = contest
        form_list = [ QuestionForm(q) for q in contest.questions ]
        form_list.append(ContestantForm)
        self.extra_context = {'object' : contest, 'question' : contest.questions[0], 'category' : contest.category,}
        super(ContestWizard, self).__init__(form_list)

    def get_template(self):
        if (self.step + 1) < len(self.form_list):
            return get_templates_from_placement('step.html', self.extra_context['placement'])
        return get_templates_from_placement('contest_form', self.extra_context['placement'])

    def process_step(self, request, form, step):
        if (step + 1) < len(self.form_list):
            self.extra_context['question'] = self.contest.questions[step]

    def done(self, request, form_list):
        # TODO get context somehow
        return contest_finish(request, {'object' : self.contest, 'category' : self.contest.category}, zip(self.contest.questions, form_list[:-1]), form_list[-1])

RESULT_FIELD = 'results'
class QuizWizard(Wizard):
    def __init__(self, quiz):
        form_list = [ QuestionForm(q) for q in quiz.questions ]
        self.quiz = quiz
        self.extra_context = {'object' : quiz, 'question' : quiz.questions[0], 'category' : quiz.category,}
        super(QuizWizard, self).__init__(form_list)

    def get_template(self):
        return get_templates_from_placement('step.html', self.extra_context['placement'])

    def process_step(self, request, form, step):
        if (step + 1) < len(self.form_list):
            self.extra_context['question'] = self.quiz.questions[step+1]

    def done(self, request, form_list):
        points = 0
        questions = []
        results = []
        for question, f in zip(self.quiz.questions, form_list):
            choices = question.choices
            if not question.allow_no_choice:
                if question.allow_multiple:
                    points += sum(c.points for c in f.cleaned_data['choice'])
                    results.append('%d:%s' % (question.id, ','.join(str(c.id) for c in f.cleaned_data['choice'])))
                else:
                    points += f.cleaned_data['choice'].points
                    results.append('%d:%s' % (question.id, f.cleaned_data['choice'].id))

        results = '|'.join(results)

        result = self.quiz.get_result(points)
        result.count += 1
        result.save()
        self.extra_context.update(
                {
                    'result' : result,
                    'points' : points,
                    'results' : results,
                    'result_field': RESULT_FIELD,
                    'result_action' : self.quiz.get_absolute_url() + slugify(_('results')) + '/'
                }
            )
        return render_to_response(
                get_templates_from_placement('result.html', self.extra_context['placement']),
                self.extra_context,
                context_instance=RequestContext(request)
            )

def result_details(request, bits, context):
    quiz = context['object']
    if not quiz.has_correct_answers:
        raise Http404
    results = request.GET.get(RESULT_FIELD, '').split('|')
    if len(results) != len(quiz.questions):
        raise Http404

    questions = []
    for question, q_res in zip(quiz.questions, results):
        q_id, id_list = q_res.split(':')
        choices = question.choices
        if question.allow_multiple:
            cl = set(id_list.split(','))
            for ch in choices:
                if str(ch.id) in cl:
                    ch.chosen = True
        else:
            for ch in choices:
                if str(ch.id) == id_list:
                    ch.chosen = True
                    break
        questions.append((question, choices))

    context['questions'] = questions

    return render_to_response(
            get_templates_from_placement('result_detail.html', context['placement']),
            context,
            context_instance=RequestContext(request)
        )

def contest(request, context):
    return contest_vote(request, context)

def conditions(request, bits, context):
    return contest_conditions(request, bits, context)

def quiz(request, context):
    quiz = context['object']
    return QuizWizard(quiz)(request, extra_context=context)

def custom_result_details(request, bits, context):
    return result_details(request, bits, context)

def cont_result(request, bits, context):
    return contest_result(request, bits, context)

