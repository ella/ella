from datetime import datetime

from django.db import models, connection
from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _, ugettext
from django.contrib.contenttypes.models import  ContentType
from django.newforms.models import InlineFormset
from django.newforms.forms import ValidationError

from ella.core.cache import get_cached_object, get_cached_list, get_cached_object_or_404
from ella.core.box import Box
from ella.core.middleware import get_current_request
from ella.core.models import Category, Listing
from ella.core.managers import RelatedManager
from ella.photos.models import Photo


ACTIVITY_NOT_YET_ACTIVE = 0
ACTIVITY_ACTIVE = 1
ACTIVITY_CLOSED = 2

class Contest(models.Model):
    """
    Contests with title, descriptions and activation
    """
    title = models.CharField(_('Title'), maxlength=200)
    slug = models.CharField(maxlength=200, db_index=True)
    category = models.ForeignKey(Category)
    text_announcement = models.TextField(_('Text with announcement'))
    text = models.TextField(_('Text'))
    text_results = models.TextField(_('Text with results'))
    active_from = models.DateTimeField(_('Active from'))
    active_till = models.DateTimeField(_('Active till'))
    photo = models.ForeignKey(Photo)

    objects = RelatedManager()

    @property
    def main_listing(self):
        try:
            return get_cached_object(
                    Listing,
                    target_ct=ContentType.objects.get_for_model(self.__class__),
                    target_id=self.id,
                    category=self.category_id
)
        except Listing.DoesNotExist:
            return None

    def get_absolute_url(self):
        listing = self.main_listing
        if listing:
            return listing.get_absolute_url()

    def get_photo(self):
        return get_cached_object(Photo, pk=self.photo_id)

    @property
    def questions(self):
        return get_cached_list(Question, contest=self)

    def __unicode__(self):
        return self.title

    def full_url(self):
        absolute_url = self.get_absolute_url()
        if absolute_url:
            return '<a href="%s">url</a>' % absolute_url
        return 'no url'
    full_url.allow_tags = True

    class Meta:
        verbose_name = _('Contest')
        verbose_name_plural = _('Contests')
        ordering = ('-active_from',)

    @property
    def current_text(self):
        return current_text(self)

    @property
    def current_activity_state(self):
        return current_activity_state(self)

    @property
    def right_choices(self):
        return '|'.join(
            '%d:%s' % (
                q.id,
                ','.join(str(c.id) for c in sorted(q.choices, key=lambda ch: ch.id) if c.points > 0)
) for q in sorted(self.questions, key=lambda q: q.id)
)

    def correct_answers(self):
        return u'<a href="%s/correct_answers/">%s - %s</a>' % (self.id, _('Correct Answers'), self.title)
    correct_answers.allow_tags = True

    def get_correct_answers(self):
        count = Contestant.objects.filter(contest=self).count()
        return Contestant.objects.filter(contest=self).filter(choices=self.right_choices).extra(select={'count_guess_difference' : 'ABS(`count_guess` - %d)' % count}).order_by('count_guess_difference')

class Quiz(models.Model):
    """
    Quizes with title, descriptions and activation options.
    """
    title = models.CharField(_('title'), maxlength=200)
    slug = models.CharField(maxlength=200, db_index=True)
    category = models.ForeignKey(Category)
    text_announcement = models.TextField(_('text with announcement'))
    text = models.TextField(_('Text'))
    text_results = models.TextField(_('Text with results'))
    active_from = models.DateTimeField(_('Active from'))
    active_till = models.DateTimeField(_('Active till'))
    photo = models.ForeignKey(Photo)

    objects = RelatedManager()

    @property
    def main_listing(self):
        try:
            return get_cached_object(
                    Listing,
                    target_ct=ContentType.objects.get_for_model(self.__class__),
                    target_id=self.id,
                    category=self.category_id
)
        except Listing.DoesNotExist:
            return None

    def full_url(self):
        absolute_url = self.get_absolute_url()
        if absolute_url:
            return '<a href="%s">url</a>' % absolute_url
        return 'no url'
    full_url.allow_tags = True


    @property
    def questions(self):
        return get_cached_list(Question, quiz=self)

    def get_absolute_url(self):
        listing = self.main_listing
        if listing:
            return listing.get_absolute_url()

    def get_photo(self):
        return get_cached_object(Photo, pk=self.photo_id)

    def get_result(self, points):
        return get_cached_object(Result, quiz=self, points_from__lte=points, points_to__gte=points)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('Quiz')
        verbose_name_plural = _('Quizes')
        ordering = ('-active_from',)

    @property
    def current_text(self):
        return current_text(self)

    @property
    def current_activity_state(self):
        return current_activity_state(self)

class Question(models.Model):
    """
    Questions used in
     * Poll
     * or Contest or Quiz related via ForeignKey
    """
    question = models.TextField(_('Question text'))
    allow_multiple = models.BooleanField(_('Allow multiple choices'), default=False)
    allow_no_choice = models.BooleanField(_('Allow no choice'), default=False)
    quiz = models.ForeignKey(Quiz, blank=True, null=True, verbose_name=_('Quiz'))
    contest = models.ForeignKey(Contest, blank=True, null=True, verbose_name=_('Contest'))

    def __unicode__(self):
        return self.question

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
        if not hasattr(self, '_form'):
            self._form = QuestionForm(self)()
        return self._form

    def is_test(self):
        if not hasattr(self, '_is_test'):
            for ch in self.choices:
                if ch.points == 0:
                    self._is_test = True
                    break
            else:
                self._is_test = False
        return self._is_test

    @property
    def choices(self):
        # FIXME - cache this, it is a queryset because of ModelChoiceField
        return self.choice_set.all()
        #return get_cached_list(Choice, question=self)

    class Meta:
        verbose_name = _('Question')
        verbose_name_plural = _('Questions')

class PollBox(Box):

    def __init__(self, obj, box_type, nodelist, template_name=None):
        super(PollBox, self).__init__(obj, box_type, nodelist, template_name)
        from ella.polls import views
        self.state = views.check_vote(get_current_request(), self.obj)

    def render(self):
        return self._render()

    def get_context(self):
        from ella.polls import views
        cont = super(PollBox, self).get_context()
        # state = views.check_vote(self._context['request'], self.obj)
        cont.update({
            'photo_slug' : self.params.get('photo_slug', ''),
            'state' : self.state,
            'state_voted' : views.POLL_USER_ALLREADY_VOTED,
            'state_just_voted' : views.POLL_USER_JUST_VOTED,
            'state_not_yet_voted' : views.POLL_USER_NOT_YET_VOTED,
            'state_no_choice' : views.POLL_USER_NO_CHOICE,
            'activity_not_yet_active' : ACTIVITY_NOT_YET_ACTIVE,
            'activity_active' : ACTIVITY_ACTIVE,
            'activity_closed' : ACTIVITY_CLOSED,
})
        return cont

    def get_cache_key(self):
        from ella.polls import views
        return super(PollBox, self).get_cache_key() + str(self.state)

    def get_cache_tests(self):
        return super(PollBox, self).get_cache_tests() + [ (Choice, lambda x: x.poll_id == self.obj.id) ]

class Poll(models.Model):
    """
    Poll model with descriptions and activation times
    """
    title = models.CharField(_('Title'), maxlength=200)
    text_announcement = models.TextField(_('Text with announcement'), blank=True, null=True)
    text = models.TextField(_('Text'), blank=True, null=True)
    text_results = models.TextField(_('Text with results'), blank=True, null=True)
    active_from = models.DateTimeField(_('Active from'), default=datetime.now, null=True, blank=True)
    active_till = models.DateTimeField(_('Active till'), null=True, blank=True)
    question = models.ForeignKey(Question, verbose_name=_('Question'), unique=True)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('Poll')
        verbose_name_plural = _('Polls')
        ordering = ('-active_from',)

    def get_question(self):
        return get_cached_object(Question, pk=self.question_id)

    def get_total_votes(self):
        return self.get_question().get_total_votes()

    def Box(self, box_type, nodelist):
        return PollBox(self, box_type, nodelist)

    @property
    def current_text(self):
        return current_text(self)

    @property
    def current_activity_state(self):
        return current_activity_state(self)

class Choice(models.Model):
    """
    Choices related to Question model ordered with respect to question
    """
    question = models.ForeignKey('Question', verbose_name=_('Question'))
    choice = models.TextField(_('Choice text'))
    points = models.IntegerField(_('Points'), blank=True, null=True)
    votes = models.IntegerField(_('Votes'), blank=True, null=True)

    def __unicode__(self):
        return self.choice

    class Meta:
        #order_with_respect_to = 'question'
        verbose_name = _('Choice')
        verbose_name_plural = _('Choices')

    def add_vote(self):
        cur = connection.cursor()
        cur.execute(UPDATE_VOTE, (self._get_pk_val(),))
        return True

    def get_percentage(self):
        t= get_cached_object(Question, pk=self.question_id).get_total_votes()
        p = 0
        if self.votes:
            p = int((100.0/t)*self.votes)
        return p

UPDATE_VOTE = '''
    UPDATE
        %(table)s
    SET
        %(col)s = COALESCE(%(col)s, 0) + 1
    WHERE
        id = %%s;
    ''' % {
        'table' : connection.ops.quote_name(Choice._meta.db_table),
        'col' : connection.ops.quote_name(Choice._meta.get_field('votes').column)
}

class Vote(models.Model):
    """
    User votes to ensure unique votes. For Polls only.
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
    name = models.CharField(_('First name'), maxlength=200)
    surname = models.CharField(_('Last name'), maxlength=200)
    email = models.EmailField(_('email'))
    phonenumber = models.CharField(_('Phone number'), maxlength=20, blank=True)
    address = models.CharField(_('Address'), maxlength=200, blank=True)
    choices = models.CharField(_('Choices'), maxlength=200, blank=True)
    count_guess = models.IntegerField(_('Count guess'))
    winner = models.BooleanField(_('Winner'), default=False)

    def __unicode__(self):
        return u'%s %s' % (self.surname, self.name)

    class Meta:
        verbose_name = _('Contestant')
        verbose_name_plural = _('Contestants')
        unique_together = (('contest', 'email',),)
        ordering = ('-datetime',)

    @property
    def points(self):
        points = 0
        for q in self.choices.split('|'):
            vs = q.split(':')
            for v in vs[1].split(','):
                points += get_cached_object(Choice, pk=v).points
        return points

class Result(models.Model):
    """
    Quiz results for skills comparation.)
    """
    quiz = models.ForeignKey(Quiz, verbose_name=_('Quiz'))
    title = models.CharField(_('Title'), maxlength=200, blank=True)
    text = models.TextField(_('Quiz results text'))
    points_from = models.IntegerField(_('Points dimension from'), null=True)
    points_to = models.IntegerField(_('Points dimension to'), null=True)
    count = models.IntegerField(_('Count'), default=0, blank=True)

    def total(self):
        res = get_cached_list(Result, quiz=self.quiz)
        return sum(r.count for r in res)

    def percentage(self):
        return self.count*100/self.total()

    def __unicode__(self):
        if self.title:
            return self.title
        return u'%s (%d - %d)' % (self.quiz, self.points_from, self.points_to)

    class Meta:
        verbose_name = _('Result')
        verbose_name_plural = _('results')

class ResultFormset(InlineFormset):

    def clean(self):
        if not self.cleaned_data:
            return self.cleaned_data

        validation_error = None
        for i in xrange(len(self.cleaned_data)):
            if self.cleaned_data[i]['points_from'] > self.cleaned_data[i]['points_to']:
                validation_error = ValidationError(ugettext('Invalid score interval %(points_from)s - %(points_to)s. Points dimension from can not be greater than point dimension to.') % self.cleaned_data[i])
                self.forms[i]._errors = {'points_to': validation_error.messages}
        if validation_error:
            raise ValidationError, ugettext('Invalid score intervals')

        intervals = [ (form_data['points_from'], form_data['points_to']) for form_data in self.cleaned_data ]
        intervals.sort()
        for i in xrange(len(intervals) - 1):
            if intervals[i][1] + 1 > intervals[i+1][0]:
                raise ValidationError, ugettext('Score %s is covered by two answers.') % (intervals[i][1])
            elif intervals[i][1] + 1 < intervals[i+1][0]:
                raise ValidationError, ugettext('Score %s is not covered by any answer.') % (intervals[i][1] + 1)
        return self.cleaned_data

from ella.ellaadmin import widgets
def formfield_for_dbfield(fields):
    def _formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in fields:
            kwargs['widget'] = widgets.RichTextAreaWidget
        return super(self.__class__, self).formfield_for_dbfield(db_field, **kwargs)
    return _formfield_for_dbfield

class ResultTabularOptions(admin.TabularInline):
    model = Result
    extra = 5
    formset = ResultFormset

class ChoiceTabularOptions(admin.TabularInline):
    model = Choice
    extra = 5

class QuestionOptions(admin.ModelAdmin):
    """
    Admin options for Question model:
        * edit inline choices
    """
    inlines = (ChoiceTabularOptions,)
    ordering = ('question',)
    search_fields = ('question',)

    formfield_for_dbfield = formfield_for_dbfield(['question'])

class ChoiceOptions(admin.ModelAdmin):
    """
    Admin options for Choices
    """
    ordering = ('question', 'choice')
    list_display = ('question', 'choice', 'votes', 'points')
    search_fields = ('choice',)

class VoteOptions(admin.ModelAdmin):
    """
    Admin options for votes
    """
    ordering = ('time',)
    list_display = ('time', 'poll', 'user', 'ip_address')

class ContestantOptions(admin.ModelAdmin):
    """
    Admin options for Contestant
    """
    ordering = ('datetime',)
    list_display = ('name', 'surname', 'user', 'datetime', 'contest', 'points', 'winner')

    formfield_for_dbfield = formfield_for_dbfield(['text_announcement', 'text', 'text_results'])

from ella.core.admin.models import ListingInlineOptions, HitCountInlineOptions
from tagging.models import TaggingInlineOptions

class QuestionInlineOptions(admin.options.InlineModelAdmin):
    model = Question
    inlines = (ChoiceTabularOptions,)
    template = 'admin/edit_inline/question_tabular.html'

    formfield_for_dbfield = formfield_for_dbfield(['question'])

class ContestOptions(admin.ModelAdmin):

    def __call__(self, request, url):
        if url and url.endswith('correct_answers'):
            from django.shortcuts import render_to_response
            pk = url.split('/')[-2]
            contest = get_cached_object_or_404(Contest, pk=pk)
            contestants = contest.get_correct_answers()
            title = u'%s \'%s\': %s' % (Contest._meta.verbose_name, contest.title, _('Correct Answers'))
            module_name = Contestant._meta.module_name
            return render_to_response('admin/correct_answers.html',
                {'contestants' : contestants, 'title' : title, 'module_name' : module_name})
        return super(ContestOptions, self).__call__(request, url)

    list_display = ('title', 'category', 'active_from', 'correct_answers', 'full_url',)
    list_filter = ('category', 'active_from',)
    search_fields = ('title', 'text_announcement', 'text', 'text_results',)
#    inlines = (QuestionInlineOptions, ListingInlineOptions, TaggingInlineOptions, HitCountInlineOptions)
    inlines = (QuestionInlineOptions, ListingInlineOptions, TaggingInlineOptions,)
    raw_id_fields = ('photo',)
    prepopulated_fields = {'slug' : ('title',)}

    formfield_for_dbfield = formfield_for_dbfield(['text_announcement', 'text', 'text_results'])

class QuizOptions(admin.ModelAdmin):
    list_display = ('title', 'category', 'active_from', 'full_url',)
    list_filter = ('category', 'active_from',)
    search_fields = ('title', 'text_announcement', 'text', 'text_results',)
#    inlines = (QuestionInlineOptions, ResultTabularOptions, ListingInlineOptions, TaggingInlineOptions, HitCountInlineOptions)
    inlines = (QuestionInlineOptions, ResultTabularOptions, ListingInlineOptions, TaggingInlineOptions,)
    raw_id_fields = ('photo',)
    prepopulated_fields = {'slug' : ('title',)}

    formfield_for_dbfield = formfield_for_dbfield(['text_announcement', 'text', 'text_results'])

class PollOptions(admin.ModelAdmin):
    formfield_for_dbfield = formfield_for_dbfield(['text_announcement', 'text', 'text_results'])
    list_display = ('title', 'question',)
    list_filter = ('active_from',)
    search_fields = ('title', 'text_announcement', 'text', 'text_results', 'question__question',)
    raw_id_fields = ('question',)

def current_text(obj):
    a = current_activity_state(obj)
    if a is ACTIVITY_NOT_YET_ACTIVE:
        return obj.text_announcement
    elif a is ACTIVITY_CLOSED:
        return obj.text_results
    else:
        return obj.text

def current_activity_state(obj):
    if obj.active_till and obj.active_till < datetime.now():
        return ACTIVITY_CLOSED
    elif obj.active_from and obj.active_from > datetime.now():
        return ACTIVITY_NOT_YET_ACTIVE
    else:
        return ACTIVITY_ACTIVE

admin.site.register(Poll, PollOptions)
admin.site.register(Contest, ContestOptions)
admin.site.register(Quiz, QuizOptions)
admin.site.register(Question, QuestionOptions)
admin.site.register(Choice, ChoiceOptions)
admin.site.register(Vote, VoteOptions)
admin.site.register(Contestant, ContestantOptions)

from ella.core.custom_urls import dispatcher

def contest(request, context):
    from ella.polls.views import contest_vote
    return contest_vote(request, context)

def conditions(request, bits, context):
    from ella.polls.views import contest_conditions
    return contest_conditions(request, bits, context)

def quiz(request, context):
    from ella.polls.views import QuizWizard
    quiz = context['object']
    return QuizWizard(quiz)(request)

def custom_result_details(request, bits, context):
    from ella.polls.views import result_details
    return result_details(request, bits, context)

def cont_result(request, bits, context):
    from ella.polls.views import contest_result
    return contest_result(request, bits, context)

dispatcher.register_custom_detail(Quiz, quiz)
dispatcher.register_custom_detail(Contest, contest)
dispatcher.register(_('results'), custom_result_details, model=Quiz)
dispatcher.register(_('result'), cont_result, model=Contest)
dispatcher.register(_('conditions'), conditions, model=Contest)

