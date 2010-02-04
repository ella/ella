from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from ella.core.models import Publishable, Author
from ella.core.cache import get_cached_object, get_cached_list


class Interviewee(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    author = models.ForeignKey(Author, null=True, blank=True)
    name = models.CharField(_('Name'), max_length=200, blank=True)
    slug = models.SlugField(_('Slug'), max_length=255)
    description = models.TextField(_('Description'), blank=True)

    class Meta:
        verbose_name = _('Interviewee')
        verbose_name_plural = _('Interviewees')
        ordering = ('name',)

    def __unicode__(self):
        if self.author_id:
            return unicode(get_cached_object(Author, pk=self.author_id))
        elif self.user_id:
            user = get_cached_object(User, pk=self.user_id)
            return user.get_full_name()
        return self.name


class Interview(Publishable):
    # Titles
    upper_title = models.CharField(_('Upper title'), max_length=255, blank=True)

    # Contents
    content = models.TextField(_('Text'))

    reply_from = models.DateTimeField(_('Reply from'))
    reply_to = models.DateTimeField(_('Reply to'))

    ask_from = models.DateTimeField(_('Ask from'))
    ask_to = models.DateTimeField(_('Ask to'))

    interviewees = models.ManyToManyField(Interviewee, verbose_name=_('Interviewees'))

    def get_text(self):
        return self.content

    ##
    # utility functions to check whether we can ask and/or reply
    ##
    def asking_started(self):
        now = datetime.now()
        return  self.ask_from <= now

    def asking_ended(self):
        now = datetime.now()
        return  self.ask_to < now

    def replying_started(self):
        now = datetime.now()
        return  self.reply_from <= now

    def replying_ended(self):
        now = datetime.now()
        return  self.reply_to < now

    def has_replies(self):
        answers = Answer.objects.filter(question__interview=self).count()
        return answers > 0

    def can_reply(self):
        return self.replying_started() and not self.replying_ended()

    def can_ask(self):
        return self.asking_started() and not self.asking_ended()

    def get_questions(self):
        """
        Return list of questions.

        Depending on the state of the interview it will either return
            questions sorted by submit date
                if asking period is over
            questions sorted by submit date descending
                if asking period isn't over yet
            only questions with answers
                if replying has started (even if it already ended)

        """
        now = datetime.now()

        q = self.question_set.all()

        if now >= self.ask_to:
            q = q.order_by('submit_date')
        else:
            q = q.order_by('-submit_date')

        if now >= self.reply_from:
            # only answered questions
            q = q.filter(answer__pk__isnull=False).distinct()

        # TODO: caching
        return q

    def unanswered_questions(self):
        # TODO: caching
        q = self.question_set.all().order_by('submit_date').filter(answer__id__isnull=True)
        return q

    def get_interviewees(self, user):
        " Get interviews that the current user can answer in behalf of. "
        if not user.is_authenticated() or not self.can_reply():
            interviewees = []
        else:
            if user.has_perm('interviews.add_answer'):
                interviewees = get_cached_list(Interviewee, interview__pk=self.pk)
            else:
                interviewees = get_cached_list(Interviewee, interview__pk=self.pk, user=user)
        return interviewees

    def get_description(self):
        " Override Publishable.get_description. "
        return self.description

    class Meta:
        verbose_name = _('Interview')
        verbose_name_plural = _('Interviews')
        ordering = ('-ask_from',)

    def __unicode__(self):
        return self.title


class Question(models.Model):
    interview = models.ForeignKey(Interview)
    content = models.TextField(_('Question text'))

    # author if is authorized
    user = models.ForeignKey(User, verbose_name=_('authorized author'), blank=True, null=True, related_name='interview_question_set')
    # author otherwise
    nickname = models.CharField(_("anonymous author's nickname"), max_length=200, blank=True)
    email = models.EmailField(_('authors email (optional)'), blank=True)

    # authors ip address
    ip_address = models.CharField(_('ip address'), max_length=20, blank=True, null=True)

    # comment metadata
    submit_date = models.DateTimeField(_('date/time submitted'), default=datetime.now, editable=False)
    is_public = models.BooleanField(_('is public'), default=True)

    @property
    def author(self):
        if self.user_id:
            user = get_cached_object(User, pk=self.user_id)
            return user.username
        return self.nickname

    @property
    def answers(self):
        return get_cached_list(Answer, question__pk=self.pk)

    def answered(self):
        return bool(self.answers)
    answered.short_description= _('Answered')
    answered.boolean = True

    class Meta:
        ordering = ('submit_date',)
        verbose_name = _('Question')
        verbose_name_plural = _('Questions')

    def __unicode__(self):
        return self.content[:20]


class Answer(models.Model):
    question = models.ForeignKey(Question)
    interviewee = models.ForeignKey(Interviewee)

    submit_date = models.DateTimeField(_('date/time submitted'), auto_now_add=True, editable=False)
    content = models.TextField(_('Answer text'))

    class Meta:
        verbose_name = _('Answer')
        verbose_name_plural = _('Answer')

