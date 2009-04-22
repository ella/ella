from datetime import datetime
import time

from django.db import models, connection
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.conf import settings

from ella.core.models import Publishable
from ella.core.cache import get_cached_object, get_cached_list
from ella.core.box import Box
from ella.core.models import Category, Author
from ella.core.managers import RelatedManager
from ella.photos.models import Photo

ACTIVITY_NOT_YET_ACTIVE = 0
ACTIVITY_ACTIVE = 1
ACTIVITY_CLOSED = 2
DOUBLE_RENDER = getattr(settings, 'DOUBLE_RENDER', False)

UPDATE_VOTE = '''
    UPDATE
        %(table)s
    SET
        %(col)s = COALESCE(%(col)s, 0) + 1
    WHERE
        id = %%s;
    '''

POLLS_IP_VOTE_TRESHOLD = 10 * 60


class PollBox(Box):

    can_double_render = True

    def prepare(self, context):
        super(PollBox, self).prepare(context)
        SECOND_RENDER = context.get('SECOND_RENDER', False)
        self.state = None
        if DOUBLE_RENDER and SECOND_RENDER or context.has_key('request'):
            from ella.polls import views
            self.state = views.poll_check_vote(context['request'], self.obj)

    def get_context(self):
        from ella.polls import views
        cont = super(PollBox, self).get_context()
        # state = views.poll_check_vote(self._context['request'], self.obj)
        cont.update({
            'photo_slug' : self.params.get('photo_slug', ''),
            'state' : self.state,
            'state_voted' : views.POLL_USER_ALLREADY_VOTED,
            'state_just_voted' : views.POLL_USER_JUST_VOTED,
            'state_not_yet_voted' : views.POLL_USER_NOT_YET_VOTED,
            'state_no_choice' : views.POLL_USER_NO_CHOICE,
            'activity_not_yet_active' : ACTIVITY_NOT_YET_ACTIVE,
            'activity_active' : ACTIVITY_ACTIVE,
            'activity_closed' : ACTIVITY_CLOSED,})
        return cont


class QuizBox(Box):

    def get_context(self):
        "Updates box context with photo-specific variables."
        from ella.polls.views import QuestionForm
        cont = super(QuizBox, self).get_context()
        questions = self.obj.questions
        cont['questions'] = questions
        cont['form'] = QuestionForm(questions[0])(prefix='0')
        return cont


class BasePoll(models.Model):

    text_announcement = models.TextField(_('Text with announcement'))
    text = models.TextField(_('Text'))
    text_results = models.TextField(_('Text with results'))
    active_from = models.DateTimeField(_('Active from'))
    active_till = models.DateTimeField(_('Active till'))

    class Meta:
        abstract = True

    @property
    def current_text(self):
        """
        Objects text content depends on its current life-cycle stage
        """
        a = self.current_activity_state
        if a is ACTIVITY_NOT_YET_ACTIVE:
            return self.text_announcement
        elif a is ACTIVITY_CLOSED:
            return self.text_results
        else:
            return self.text

    @property
    def current_activity_state(self):
        """
        Objects current life-cycle stage
        """
        if self.active_till and self.active_till < datetime.now():
            return ACTIVITY_CLOSED
        elif self.active_from and self.active_from > datetime.now():
            return ACTIVITY_NOT_YET_ACTIVE
        else:
            return ACTIVITY_ACTIVE

    def is_active(self):
        """
        Returns True if the object is in the ACTIVE life-cycle stage. Otherwise returns False
        """
        if self.current_activity_state == ACTIVITY_ACTIVE:
            return True
        return False


class Poll(BasePoll):

    title = models.CharField(_('Title'), max_length=200)
    question = models.ForeignKey('Question', verbose_name=_('Question'), unique=True)

    box_class = PollBox

    def get_question(self):
        return get_cached_object(Question, pk=self.question_id)

    def get_total_votes(self):
        return self.get_question().get_total_votes()
    get_total_votes.short_description = _('Votes in total')

    def __unicode__(self):
        return self.title

    def vote(self, choice, user=None, ip_address=None):
        # create Vote object
        vote = Vote(poll=self, user=user, ip_address=ip_address)
        vote.save()
        # increment votes at Choice object
        choice.add_vote()

    def check_vote_by_user(self, user):
        return Vote.objects.filter(poll=self, user=user).count() > 0

    def check_vote_by_ip_address(self, ip_address):
        treshold = datetime.fromtimestamp(time.time() - POLLS_IP_VOTE_TRESHOLD)
        return Vote.objects.filter(poll=self, ip_address=ip_address, time__gte=treshold).count() > 0

    class Meta:
        verbose_name = _('Poll')
        verbose_name_plural = _('Polls')
        ordering = ('-active_from',)


class Contest(BasePoll, Publishable):

    objects = RelatedManager()

    @property
    def questions(self):
        return get_cached_list(Question, contest=self)

    @property
    def right_choices(self):
        return '|'.join(
            '%d:%s' % (
                q.id,
                ','.join(str(c.id) for c in sorted(q.choices, key=lambda ch: ch.id) if c.points > 0)
            ) for q in sorted(self.questions, key=lambda q: q.id)
        )

    def correct_answers(self):
        """
        Admin's list column with a link to the list of contestants with correct answers on the current contest
        """
        return mark_safe(u'<a href="%s/correct_answers/">%s - %s</a>' % (self.id, _('Correct Answers'), self.title))
    correct_answers.allow_tags = True

    def get_all_answers_count(self):
        return Contestant.objects.filter(contest=self).count()
    get_all_answers_count.short_description = _('Participants in total')

    def get_correct_answers(self):
        """
        Returns queryset of contestants with correct answers on the current contest
        """
        count = Contestant.objects.filter(contest=self).count()
        return (Contestant.objects
            .filter(contest=self)
            .filter(choices=self.right_choices)
            .extra(select={'count_guess_difference': 'ABS(%s - %d)' % (connection.ops.quote_name('count_guess'), count)})
            .order_by('count_guess_difference'))

    def get_description(self):
        return self.text_announcement

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('Contest')
        verbose_name_plural = _('Contests')
        ordering = ('-active_from',)


class Quiz(BasePoll, Publishable):

    has_correct_answers = models.BooleanField(_('Has correct answers'))

    box_class = QuizBox

    objects = RelatedManager()

    @property
    def questions(self):
        return get_cached_list(Question, quiz=self)

    def get_result(self, points):
        """
        Returns cached quiz result by the reached points
        """
        return get_cached_object(Result, quiz=self, points_from__lte=points, points_to__gte=points)

    def get_description(self):
        return self.text_announcement

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('Quiz')
        verbose_name_plural = _('Quizes')
        ordering = ('-active_from',)


class Question(models.Model):

    question = models.TextField(_('Question text'))
    allow_multiple = models.BooleanField(_('Allow multiple choices'), default=False)
    allow_no_choice = models.BooleanField(_('Allow no choice'), default=False)
    quiz = models.ForeignKey(Quiz, blank=True, null=True, verbose_name=_('Quiz'))
    contest = models.ForeignKey(Contest, blank=True, null=True, verbose_name=_('Contest'))

    @property
    def choices(self):
        # FIXME - cache this, it is a queryset because of ModelChoiceField
        return self.choice_set.all()
        #return get_cached_list(Choice, question=self)

    def get_total_votes(self):
        if not hasattr(self, '_total_votes'):
            total_votes = 0
            for choice in self.choices:
                if choice.votes:
                    total_votes += choice.votes
            self._total_votes = total_votes
        return self._total_votes

    def form(self):
        from ella.polls.views import QuestionForm
        return QuestionForm(self)()

    def is_test(self):
        if not hasattr(self, '_is_test'):
            for ch in self.choices:
                if ch.points == 0:
                    self._is_test = True
                    break
            else:
                self._is_test = False
        return self._is_test

    def __unicode__(self):
        return self.question

    class Meta:
        verbose_name = _('Question')
        verbose_name_plural = _('Questions')


class Choice(models.Model):

    question = models.ForeignKey('Question', verbose_name=_('Question'))
    choice = models.TextField(_('Choice text'))
    points = models.IntegerField(_('Points'), blank=False, null=True)
    votes = models.IntegerField(_('Votes'), blank=True, null=True)

    def add_vote(self):
        """
        Add a vote dirrectly to DB
        """
        query = UPDATE_VOTE % {
            'table' : connection.ops.quote_name(self._meta.db_table), 
            'col' : connection.ops.quote_name(self._meta.get_field('votes').column)}
        cur = connection.cursor()
        cur.execute(query, (self.pk,))
        return True

    def get_percentage(self):
        """
        Compute and return percentage representation of choice object to its question's total votes
        """
        t = get_cached_object(Question, pk=self.question_id).get_total_votes()
        p = 0
        if self.votes:
            p = int((100.0/t)*self.votes)
        return p

    def __unicode__(self):
        return self.choice

    class Meta:
        verbose_name = _('Choice')
        verbose_name_plural = _('Choices')


class Vote(models.Model):
    """
    User votes records to ensure unique votes. For Polls only.
    """
    poll = models.ForeignKey(Poll, verbose_name=_('Poll'))
    user = models.ForeignKey(User, blank=True, null=True, verbose_name=_('User'))
    time = models.DateTimeField(_('Time'), auto_now=True)
    ip_address = models.IPAddressField(_('IP Address'), null=True)

    def __unicode__(self):
        return u'%s' % self.time

    class Meta:
        verbose_name = _('Vote')
        verbose_name_plural = _('Votes')
        ordering = ('-time',)


class Contestant(models.Model):
    """
    Contestant info.
    """
    contest = models.ForeignKey(Contest, verbose_name=_('Contest'))
    datetime = models.DateTimeField(_('Date and time'), auto_now_add=True)
    user = models.ForeignKey(User, null=True, blank=True, verbose_name=_('User'))
    name = models.CharField(_('First name'), max_length=200)
    surname = models.CharField(_('Last name'), max_length=200)
    email = models.EmailField(_('email'))
    phonenumber = models.CharField(_('Phone number'), max_length=20, blank=True)
    address = models.CharField(_('Address'), max_length=200, blank=True)
    choices = models.TextField(_('Choices'), blank=True)
    count_guess = models.IntegerField(_('Count guess'))
    winner = models.BooleanField(_('Winner'), default=False)

    @property
    def points(self):
        """
        Parse choices represented as a string and returns reached points count
        """
        points = 0
        for q in self.choices.split('|'):
            vs = q.split(':')
            for v in vs[1].split(','):
                points += get_cached_object(Choice, pk=v).points
        return points

    def __unicode__(self):
        return u'%s %s' % (self.surname, self.name)

    class Meta:
        verbose_name = _('Contestant')
        verbose_name_plural = _('Contestants')
        unique_together = (('contest', 'email',),)
        ordering = ('-datetime',)


class Result(models.Model):
    """
    Quiz results for knowledge comparation.)
    """
    quiz = models.ForeignKey(Quiz, verbose_name=_('Quiz'))
    title = models.CharField(_('Title'), max_length=200, blank=True)
    text = models.TextField(_('Quiz results text'))
    points_from = models.IntegerField(_('Points dimension from'), null=True)
    points_to = models.IntegerField(_('Points dimension to'), null=True)
    count = models.IntegerField(_('Count'), blank=False, null=False)

    def total(self):
        """
        Returns count of displayed quiz results
        """
        res = get_cached_list(Result, quiz=self.quiz)
        return sum(r.count for r in res)

    def percentage(self):
        """
        Returns percentage ratio of current Result views
        """
        return self.count*100/self.total()

    def __unicode__(self):
        if self.title:
            return self.title
        return u'%s (%d - %d)' % (self.quiz, self.points_from, self.points_to)

    class Meta:
        verbose_name = _('Result')
        verbose_name_plural = _('results')

