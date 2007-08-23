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
from ella.polls.models import Poll, Contest, Contestant, Quiz, Result, Choice, Vote

# POLLS specific settings
POLLS_COOKIE_NAME = getattr(settings, 'POLLS_COOKIE_NAME', 'polls_voted')
POLLS_JUST_VOTED_COOKIE_NAME = getattr(settings, 'POLLS_JUST_VOTED_COOKIE_NAME', 'polls_just_voted_voted')
POLLS_MAX_COOKIE_LENGTH = getattr(settings, 'POLLS_MAX_COOKIE_LENGTH', 20)
POLLS_MAX_COOKIE_AGE = getattr(settings, 'POLLS_MAX_COOKIE_AGE', 3600)

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

    form = QuestionForm(poll.question, request.POST)
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

@require_POST
@transaction.commit_on_success
def contest_vote(request, contest_id):
    # get contest content type
    contest_ct = ContentType.objects.get_for_model(Contest)
    # get current contest object
    contest = get_cached_object_or_404(contest_ct, pk=contest_id)
    forms = []
    forms_are_valid = True
    # questions forms
    for question in contest.question_set.all():
        form = QuestionForm(question, request.POST or None, prefix=str(question.id))
        if not form.is_valid() and forms_are_valid:
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
        # CHECK pouze na unikatni email ci USER
        kwa = contestant_form.cleaned_data
        # building choices field value
        choices = []
        for question, form in forms:
            if question.allow_multiple:
                chs = []
                for choice in form.cleaned_data['choice']:
                    choice.add_vote()
                    chs.append(str(choice.id))
                ch = str(','.join(chs))
            else:
                form.cleaned_data['choice'].add_vote()
                ch = str(form.cleaned_data['choice'].id)
            choices.append(':'.join((str(question.id), ch)))
        kwa['choices'] = ';'.join(choices)
        if request.user.is_authenticated():
            kwa['user'] = request.user
        contestant = Contestant(contest=contest, **kwa)
        contestant.save()
        return HttpResponseRedirect(get_next_url(request))
    return render_to_response('polls/contest_form.html', {
        'forms' : forms,
        'contestant_form' : contestant_form},
        context_instance=RequestContext(request))

#@request_POST
@transaction.commit_on_success
def quiz_vote(request, quiz_id):
    # get quiz content type
    quiz_ct = ContentType.objects.get_for_model(Quiz)
    # get current quiz object
    quiz = get_cached_object_or_404(quiz_ct, pk=quiz_id)
    forms = []
    forms_are_valid = True
    # questions forms
    for question in quiz.question_set.all():
        form = QuestionForm(question, request.POST or None, prefix=str(question.id))
        if not form.is_valid() and forms_are_valid:
            forms_are_valid = False
        forms.append((question, form))
    if forms_are_valid:
        # points
        points = 0
        for question, form in forms:
            if question.allow_multiple:
                for choice in form.cleaned_data['choice']:
                    points += choice.points
            else:
                points += form.cleaned_data['choice'].points
        # retriev quiz results
        try:
            results = Result.objects.get(quiz=quiz, points_from__gte=points, points_to__lt=points)
        except Result.DoesNotExist:
            # TODO LOG
            # ale chybu polykame, redaktor muze zadat blbe rozsahy
            pass
        return HttpResponseRedirect(get_next_url(request))
    return render_to_response('polls/quiz_form.html',
        {'forms' : forms},
        context_instance=RequestContext(request))

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

class QuestionForm(forms.Form):
    """
    Question form with all its choices
    """
    def choices(self):
        field = self['choice']
        for choice, input in  zip(field.field.queryset, field.as_widget(field.field.widget)):
            yield (choice, input)

    def __init__(self, question, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        if question.allow_multiple:
            self.fields['choice'] = forms.ModelMultipleChoiceField(
                queryset=question.choice_set.all(),
                widget=forms.CheckboxSelectMultiple)
        else:
            self.fields['choice'] = forms.ModelChoiceField(
                queryset=question.choice_set.all(),
                widget=MyRadioSelect,
                empty_label=None)



class ContestantForm(forms.Form):
    """
    Contestant form
    """
    name = Contestant._meta.get_field('name').formfield()
    surname = Contestant._meta.get_field('surname').formfield()
    email = Contestant._meta.get_field('email').formfield()
    phonenumber = Contestant._meta.get_field('phonenumber').formfield()
    address = Contestant._meta.get_field('address').formfield()
