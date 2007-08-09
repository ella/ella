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
POLLS_MAX_COOKIE_LENGTH = getattr(settings, 'POLLS_MAX_COOKIE_LENGTH', 20)
POLLS_MAX_COOKIE_AGE = getattr(settings, 'POLLS_MAX_COOKIE_AGE', 3600)

def check_vote(request, poll):
    # authenticated user - check session
    if request.user.is_authenticated():
        sess = request.session.get(POLLS_COOKIE_NAME, [])
        if (poll_ct.id, poll.id) in sess:
            return HttpResponseRedirect(url)
    # anonymous - check cookie
    else:
        cook = request.COOKIES.get(POLLS_COOKIE_NAME, '').split(',')
        if '%s:%s' % (poll_ct.id, poll.id) in cook:
            return HttpResponseRedirect(url)
    # check by DB
    try:
        user_vote = Vote.objects.get(poll=poll)
    except Exception:



#@require_POST
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

    form = QuestionForm(poll.question, request.POST or None)
    if form.is_valid():

        # choice data from form
        choice = form.cleaned_data['choice']

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
        # zaznamenat do session a pak vymazat
        # ...

        # update anti-spam - cook, sess
        if request.user.is_authenticated():
            sess = request.session.get(POLLS_COOKIE_NAME, [])
            sess.append((poll_ct.id, poll.id))
            request.session[POLLS_COOKIE_NAME] = sess
        else:
            cook = request.COOKIES.get(POLLS_COOKIE_NAME, '').split(',')
            if len(cook) > POLLS_MAX_COOKIE_LENGTH:
                cook = cook[1:]
            cook.append('%s:%s' % (poll_ct.id, poll.id))
            expires = datetime.strftime(datetime.utcnow() + timedelta(seconds=POLLS_MAX_COOKIE_AGE), "%a, %d-%b-%Y %H:%M:%S GMT")
            HttpResponseRedirect(url).set_cookie(
                POLLS_COOKIE_NAME,
                value=','.join(cook),
                max_age=POLLS_MAX_COOKIE_AGE,
                expires=expires,
                path='/',
                domain=Site.objects.get_current().domain,
                secure=None
)

        return HttpResponseRedirect(url)

    return render_to_response('polls/poll_form.html', {'form' : form, 'next' : url}, context_instance=RequestContext(request))

#@request_POST
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
        except Exception:
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

class QuestionForm(forms.Form):
    """
    Question form with all its choices
    """
    def __init__(self, question, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        if question.allow_multiple:
            self.fields['choice'] = forms.ModelMultipleChoiceField(
                queryset=question.choice_set.all(),
                widget=forms.CheckboxSelectMultiple)
        else:
            self.fields['choice'] = forms.ModelChoiceField(
                queryset=question.choice_set.all(),
                widget=forms.RadioSelect,
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
