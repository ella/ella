from django.db import models, backend, connection
from django.contrib import admin
from django.contrib.auth.models import User

class Poll(models.Model):
    """
    Poll model with descriptions and activation times
    """
    title = models.CharField(maxlength=200)
    text_announcement = models.TextField()
    text = models.TextField()
    text_results = models.TextField()
    active_from = models.DateTimeField()
    active_till = models.DateTimeField()
    question = models.ForeignKey('Question')

    def __unicode__(self):
        return self.title

class Question(models.Model):
    """
    Questions used in
     * Poll
     * or Contest or Quiz related via ForeignKey
    """
    question = models.TextField()
    allow_multiple = models.BooleanField(default=False)
    quiz = models.ForeignKey('Quiz', blank=True, null=True)
    contest = models.ForeignKey('Contest', blank=True, null=True)

    def __unicode__(self):
        return self.question

class Choice(models.Model):
    """
    Choices related to Question model ordered with respect to question
    """
    question = models.ForeignKey('Question')
    choice = models.CharField(maxlength=200)
    points = models.IntegerField(blank=True, null=True)
    votes = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return self.choice

    class Meta:
        order_with_respect_to = 'question'

    def add_vote(self):
        cur = connection.cursor()
        cur.execute(UPDATE_VOTE, (self._get_pk_val(),))
        return True

UPDATE_VOTE = '''
    UPDATE
        %(table)s
    SET
        %(col)s = COALESCE(%(col)s, 0) + 1
    WHERE
        id = %%s;
    ''' % {
        'table' : backend.quote_name(Choice._meta.db_table),
        'col' : backend.quote_name(Choice._meta.get_field('votes').column)
}

class Vote(models.Model):
    """
    User votes to ensure unique votes. For Polls only.
    """
    poll = models.ForeignKey('poll')
    user = models.ForeignKey(User, blank=True, null=True)
    time = models.DateTimeField(auto_now=True)
    ip_address = models.IPAddressField(null=True)

    def __unicode__(self):
        return u'%s' % self.time

class Contest(models.Model):
    """
    Contests with title, descriptions and activation
    """
    title = models.CharField(maxlength=200)
    text_announcement = models.TextField()
    text = models.TextField()
    text_results = models.TextField()
    active_from = models.DateTimeField()
    active_till = models.DateTimeField()

    def __unicode__(self):
        return self.title

class Contestant(models.Model):
    """
    Contestant info.
    """
    contest = models.ForeignKey('Contest')
    datetime = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, null=True, blank=True)
    name = models.CharField(maxlength=200)
    surname = models.CharField(maxlength=200)
    email = models.EmailField()
    phonenumber = models.PhoneNumberField(null=True)
    address = models.CharField(maxlength=200)
    choices = models.TextField()

    def __unicode__(self):
        return u'%s %s' % (self.surname, self.name)

class Quiz(models.Model):
    """
    Quizes with title, descriptions and activation options.
    """
    title = models.CharField(maxlength=200)
    text_announcement = models.TextField()
    text = models.TextField()
    text_results = models.TextField()
    active_from = models.DateTimeField()
    active_till = models.DateTimeField()

    def __unicode__(self):
        return self.title

class Result(models.Model):
    """
    Quiz results for skills comparation.)
    """
    quiz = models.ForeignKey('Quiz')
    title = models.CharField(maxlength=200)
    text = models.TextField()
    points_from = models.IntegerField(null=True)
    points_to = models.IntegerField(null=True)
    count = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return self.title

class QuestionOptions(admin.ModelAdmin):
    """
    Admin options for Question model:
        * edit inline choices
    """
    inlines = [admin.TabularInline(Choice, extra=1)]
    ordering = ('question',)
    #list_displpay = ('',)

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
