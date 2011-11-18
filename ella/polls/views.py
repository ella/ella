from datetime import datetime, timedelta
from itertools import chain, cycle

from django.shortcuts import render_to_response
from django.utils.translation import ugettext, ugettext_lazy as _
from django.http import HttpResponseRedirect, Http404
from django import forms
from django.views.decorators.http import require_POST
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from django.template import RequestContext
from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode
from django.contrib.formtools.wizard import FormWizard
from django.views.decorators.csrf import csrf_protect

from ella.core.cache import get_cached_object_or_404
from ella.core.views import get_templates_from_placement
from ella.polls.models import Poll, Contestant, Survey
from ella.polls.conf import polls_settings

def get_next_url(request):
    """
    Return URL for redirection

    Try to get it from:
        * POST param 'next'
        * HTTP_REFERER
    """
    if 'next' in request.POST: # and request.POST['next'].startswith('/'):
        return request.POST['next']
    else:
        return request.META.get('HTTP_REFERER', '/')


def poll_check_vote(request, poll):
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
    sess_jv = request.session.get(polls_settings.POLL_JUST_VOTED_COOKIE_NAME, [])
    # removing just voted info from session
    if poll.id in sess_jv:
        del request.session[polls_settings.POLL_JUST_VOTED_COOKIE_NAME]
        # TODO - del just my poll, not the entire list !
        return polls_settings.USER_JUST_VOTED
    # removing no vote info from session
    sess_nv = request.session.get(polls_settings.POLL_NO_CHOICE_COOKIE_NAME, [])
    if poll.id in sess_nv:
        del request.session[polls_settings.POLL_NO_CHOICE_COOKIE_NAME]
        # TODO - del just my poll, not the entire list !
        return polls_settings.USER_NO_CHOICE
    # authenticated user - check session
    if request.user.is_authenticated():
        sess = request.session.get(polls_settings.POLL_COOKIE_NAME, [])
        if poll.id in sess:
            return polls_settings.USER_ALLREADY_VOTED
        # otherwise check Vote object - just for sure
        if poll.check_vote_by_user(request.user):
            return polls_settings.USER_ALLREADY_VOTED
        return polls_settings.USER_NOT_YET_VOTED
    # anonymous - check cookie
    else:
        cook = request.COOKIES.get(polls_settings.POLL_COOKIE_NAME, '').split(',')
        if str(poll.id) in cook:
            return polls_settings.USER_ALLREADY_VOTED
        ip_address = request.META['REMOTE_ADDR']
        # otherwise check Vote object - just for sure
        if poll.check_vote_by_ip_address(ip_address):
            return polls_settings.USER_ALLREADY_VOTED
        return polls_settings.USER_NOT_YET_VOTED

def survey_check_vote(request, survey):
    sess_jv = request.session.get(polls_settings.SURVEY_JUST_VOTED_COOKIE_NAME, [])
    # removing just voted info from session
    if survey.id in sess_jv:
        del request.session[polls_settings.SURVEY_JUST_VOTED_COOKIE_NAME]
        # TODO - del just my poll, not the entire list !
        return polls_settings.USER_JUST_VOTED
    # removing no vote info from session
    sess_nv = request.session.get(polls_settings.SURVEY_NO_CHOICE_COOKIE_NAME, [])
    if survey.id in sess_nv:
        del request.session[polls_settings.SURVEY_NO_CHOICE_COOKIE_NAME]
        # TODO - del just my poll, not the entire list !
        return polls_settings.USER_NO_CHOICE
    # authenticated user - check session
    if request.user.is_authenticated():
        sess = request.session.get(polls_settings.SURVEY_COOKIE_NAME, [])
        if survey.id in sess:
            return polls_settings.USER_ALLREADY_VOTED
        # otherwise check Vote object - just for sure
        if survey.check_vote_by_user(request.user):
            return polls_settings.USER_ALLREADY_VOTED
        return polls_settings.USER_NOT_YET_VOTED
    # anonymous - check cookie
    else:
        cook = request.COOKIES.get(polls_settings.SURVEY_COOKIE_NAME, '').split(',')
        if str(survey.id) in cook:
            return polls_settings.USER_ALLREADY_VOTED
        ip_address = request.META['REMOTE_ADDR']
        # otherwise check Vote object - just for sure
        if survey.check_vote_by_ip_address(ip_address):
            return polls_settings.USER_ALLREADY_VOTED
        return polls_settings.USER_NOT_YET_VOTED

@csrf_protect
@require_POST
@transaction.commit_on_success
def poll_vote(request, poll_id):

    poll_ct = ContentType.objects.get_for_model(Poll)
    poll = get_cached_object_or_404(poll_ct, pk=poll_id)

    url = get_next_url(request)

    # activity check
    if not poll.is_active():
        return HttpResponseRedirect(url)

    # vote check
    if poll_check_vote(request, poll) != polls_settings.USER_NOT_YET_VOTED:
        return HttpResponseRedirect(url)

    form = QuestionForm(poll.question)(request.POST)

    # invalid input
    if not form.is_valid():
        # no choice selected error - via session
        sess_nv = request.session.get(polls_settings.POLL_NO_CHOICE_COOKIE_NAME, [])
        sess_nv.append(poll.id)
        request.session[polls_settings.POLL_NO_CHOICE_COOKIE_NAME] = sess_nv
        return HttpResponseRedirect(url)

    # vote save
    kwa = {}
    if request.user.is_authenticated():
        kwa['user'] = request.user
    kwa['ip_address'] = request.META['REMOTE_ADDR']
    poll.vote(form.cleaned_data['choice'], **kwa)

    # just voted info session update
    sess_jv = request.session.get(polls_settings.POLL_JUST_VOTED_COOKIE_NAME, [])
    sess_jv.append(poll.id)
    request.session[polls_settings.POLL_JUST_VOTED_COOKIE_NAME] = sess_jv

    response = HttpResponseRedirect(url)

    # authenticated user vote - session update
    if request.user.is_authenticated():
        sess = request.session.get(polls_settings.POLL_COOKIE_NAME, [])
        sess.append(poll.id)
        request.session[polls_settings.POLL_COOKIE_NAME] = sess
    # annonymous user vote - cookies update
    else:
        cook = request.COOKIES.get(polls_settings.POLL_COOKIE_NAME, '').split(',')
        if len(cook) > polls_settings.POLL_MAX_COOKIE_LENGTH:
            cook = cook[1:]
        cook.append(str(poll.id))
        expires = datetime.strftime(datetime.utcnow() + timedelta(seconds=polls_settings.POLL_MAX_COOKIE_AGE), "%a, %d-%b-%Y %H:%M:%S GMT")
        response.set_cookie(
            polls_settings.POLL_COOKIE_NAME,
            value=','.join(cook),
            max_age=polls_settings.POLL_MAX_COOKIE_AGE,
            expires=expires,
            path='/',
            domain=Site.objects.get_current().domain,
            secure=None
        )

    return response


@csrf_protect
@require_POST
@transaction.commit_on_success
def survey_vote(request, survey_id):

    survey_ct = ContentType.objects.get_for_model(Survey)
    survey = get_cached_object_or_404(survey_ct, pk=survey_id)

    url = get_next_url(request)

    # activity check
    if not survey.current_activity_state == polls_settings.ACTIVITY_ACTIVE:
        return HttpResponseRedirect(url)

    # vote check
    if survey_check_vote(request, survey) != polls_settings.USER_NOT_YET_VOTED:
        return HttpResponseRedirect(url)

    form = QuestionForm(survey)(request.POST)

    # invalid input
    if not form.is_valid():
        # no choice selected error - via session
        sess_nv = request.session.get(polls_settings.SURVEY_NO_CHOICE_COOKIE_NAME, [])
        sess_nv.append(survey.id)
        request.session[polls_settings.SURVEY_NO_CHOICE_COOKIE_NAME] = sess_nv
        return HttpResponseRedirect(url)

    # vote save
    kwa = {}
    if request.user.is_authenticated():
        kwa['user'] = request.user
    kwa['ip_address'] = request.META['REMOTE_ADDR']
    survey.vote(form.cleaned_data['choice'], **kwa)

    # just voted info session update
    sess_jv = request.session.get(polls_settings.SURVEY_JUST_VOTED_COOKIE_NAME, [])
    sess_jv.append(survey.id)
    request.session[polls_settings.SURVEY_JUST_VOTED_COOKIE_NAME] = sess_jv

    response = HttpResponseRedirect(url)

    # authenticated user vote - session update
    if request.user.is_authenticated():
        sess = request.session.get(polls_settings.SURVEY_COOKIE_NAME, [])
        sess.append(survey.id)
        request.session[polls_settings.SURVEY_COOKIE_NAME] = sess
    # annonymous user vote - cookies update
    else:
        cook = request.COOKIES.get(polls_settings.SURVEY_COOKIE_NAME, '').split(',')
        if len(cook) > polls_settings.SURVEY_MAX_COOKIE_LENGTH:
            cook = cook[1:]
        cook.append(str(survey.id))
        expires = datetime.strftime(datetime.utcnow() + timedelta(seconds=polls_settings.SURVEY_MAX_COOKIE_AGE), "%a, %d-%b-%Y %H:%M:%S GMT")
        response.set_cookie(
            polls_settings.SURVEY_COOKIE_NAME,
            value=','.join(cook),
            max_age=polls_settings.SURVEY_MAX_COOKIE_AGE,
            expires=expires,
            path='/',
            domain=Site.objects.get_current().domain,
            secure=None
        )

    return response

@csrf_protect
@transaction.commit_on_success
def contest_vote(request, context):

    contest = context['object']

    forms = []
    forms_are_valid = True
    # question forms
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
            'activity_not_yet_active' : polls_settings.ACTIVITY_NOT_YET_ACTIVE,
            'activity_active' : polls_settings.ACTIVITY_ACTIVE,
            'activity_closed' : polls_settings.ACTIVITY_CLOSED
        })
    return render_to_response(
        get_templates_from_placement('form.html', context['placement']),
        context,
        context_instance=RequestContext(request)
    )


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
            yield mark_safe(u'<label>%s %s</label>' % (cb.render(name, option_value), force_unicode(option_label)))


class MyRadioSelect(forms.RadioSelect):
    def render(self, name, value, attrs=None, choices=()):
        return self.get_renderer(name, value, attrs, choices)

def fudge_choice_percentages(choices):
    percent_sum = 0
    choice_list = list(choices)
    for choice in choice_list:
        choice.percentage = choice.get_percentage()
        percent_sum += choice.percentage

    choice_iter = cycle(choice_list)
    step = cmp(100, percent_sum)
    while percent_sum != 100:
        choice = choice_iter.next()
        choice.percentage += step
        percent_sum += step

    return choice_list

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
            choice_list = fudge_choice_percentages(field.field.queryset)
            for choice, input in  zip(choice_list, field.as_widget(field.field.widget)):
                yield choice, input

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

def contest_result(request, context):
    return render_to_response(
        get_templates_from_placement('result.html', context['placement']),
        context,
        context_instance=RequestContext(request)
    )

def contest_conditions(request, context):
    return render_to_response(
        get_templates_from_placement('conditions.html', context['placement']),
        context,
        context_instance=RequestContext(request)
    )

RESULT_FIELD = 'results'
class QuizWizard(FormWizard):
    def __init__(self, quiz):
        form_list = [ QuestionForm(q) for q in quiz.questions ]
        super(QuizWizard, self).__init__(form_list)
        self.quiz = quiz
        self.extra_context = {'object' : quiz, 'question' : quiz.questions[0], 'category' : quiz.category,}
        # ?? ?? ?? ??
        #super(QuizWizard, self).__init__(form_list)
        # ?? ?? ?? ??

    def get_template(self, step):
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

def result_details(request, context):
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

@csrf_protect
def contest(request, context):
    return contest_vote(request, context)

@csrf_protect
def quiz(request, context):
    quiz = context['object']
    return QuizWizard(quiz)(request, extra_context=context)


