from django.db import models, connection
from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import  ContentType

from ella.core.cache import get_cached_object, get_cached_list
from ella.core.box import Box
from ella.core.models import Category, Listing

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

    @property
    def questions(self):
        return get_cached_list(Question, contest=self)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('Contest')
        verbose_name_plural = _('Contests')
        ordering = ('-active_from',)

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

    @property
    def questions(self):
        return get_cached_list(Question, contest=self)

    def get_absolute_url(self):
        listing = self.main_listing
        if listing:
            return listing.get_absolute_url()

    def get_result(self, points):
        return get_cached_object(Result, quiz=self, points_from__lte=points, points_to__gt=points)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('Quiz')
        verbose_name_plural = _('Quizes')
        ordering = ('-active_from',)

class Question(models.Model):
    """
    Questions used in
     * Poll
     * or Contest or Quiz related via ForeignKey
    """
    question = models.TextField(_('Question text'))
    allow_multiple = models.BooleanField(_('Allow multiple choices'), default=False)
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

    @property
    def choices(self):
        return get_cached_list(Choice, question=self)

    class Meta:
        verbose_name = _('Question')
        verbose_name_plural = _('Questions')

class PollBox(Box):
   def get_context(self):
        from ella.polls import views
        cont = super(PollBox, self).get_context()
        # state = views.check_vote(self._context['request'], self.obj)
        cont.update({
            'state' : views.check_vote(self._context['REQUEST'], self.obj),
            'state_voted' : views.POLL_USER_ALLREADY_VOTED,
            'state_just_voted' : views.POLL_USER_JUST_VOTED,
            'state_not_yet_voted' : views.POLL_USER_NOT_YET_VOTED})
        return cont

class Poll(models.Model):
    """
    Poll model with descriptions and activation times
    """
    title = models.CharField(_('Title'), maxlength=200)
    text_announcement = models.TextField(_('Text with announcement'))
    text = models.TextField(_('Text'))
    text_results = models.TextField(_('Text with results'))
    active_from = models.DateTimeField(_('Active from'))
    active_till = models.DateTimeField(_('Active till'))
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

class Choice(models.Model):
    """
    Choices related to Question model ordered with respect to question
    """
    question = models.ForeignKey('Question', verbose_name=_('Question'))
    choice = models.CharField(_('Choice text'), maxlength=200)
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
    phonenumber = models.PhoneNumberField(_('Phone number'), null=True)
    address = models.CharField(_('Address'), maxlength=200)
    choices = models.TextField(_('Choices'))

    def __unicode__(self):
        return u'%s %s' % (self.surname, self.name)

    class Meta:
        verbose_name = _('Contestant')
        verbose_name_plural = _('Contestants')
        ordering = ('-datetime',)

class Result(models.Model):
    """
    Quiz results for skills comparation.)
    """
    quiz = models.ForeignKey(Quiz, verbose_name=_('Quiz'))
    title = models.CharField(_('Title'), maxlength=200)
    text = models.TextField(_('Quiz results text'))
    points_from = models.IntegerField(_('Points dimension from'), null=True)
    points_to = models.IntegerField(_('Points dimension to'), null=True)
    count = models.IntegerField(_('Points count'), default=0, blank=True)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('Result')
        verbose_name_plural = _('results')

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
    ordering = ('contest', 'datetime')
    list_display = ('name', 'surname', 'user', 'datetime', 'contest', 'choices')

admin.site.register(Poll)
admin.site.register(Contest)
admin.site.register(Quiz)
admin.site.register(Question, QuestionOptions)
admin.site.register(Choice, ChoiceOptions)
admin.site.register(Vote, VoteOptions)
admin.site.register(Contestant, ContestantOptions)
admin.site.register(Result)
