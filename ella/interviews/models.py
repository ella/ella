from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from ella.photos.models import Photo
from ella.core.managers import RelatedManager
from ella.core.cache import get_cached_object, get_cached_list
from ella.core.models import Listing, Category, Author, Source

class Interviewee(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    author = models.ForeignKey(Author, null=True, blank=True)
    name = models.CharField(_('Name'), max_length=200, blank=True)
    slug = models.CharField(_('Slug'), max_length=200)
    description = models.TextField(_('Description'), blank=True)

    class Meta:
        verbose_name = _('Interviewee')
        verbose_name_plural = _('Interviewees')
        ordering = ('name',)

    def __unicode__(self):
        if self.author_id:
            return unicode(get_cached_object(Author, pk=self.author_id))
        elif self.user_id:
            return unicode(get_cached_object(User, pk=self.user_id))
        return self.name


class Interview(models.Model):
    # Titles
    title = models.CharField(_('Title'), max_length=255)
    upper_title = models.CharField(_('Upper title'), max_length=255, blank=True)
    slug = models.CharField(_('Slug'), db_index=True, max_length=255)

    # Contents
    perex = models.TextField(_('Perex'))
    content = models.TextField(_('Text'))

    reply_from = models.DateTimeField(_('Reply from'))
    reply_to = models.DateTimeField(_('Reply to'))

    ask_from = models.DateTimeField(_('Ask from'))
    ask_to = models.DateTimeField(_('Ask to'))

    # Authors and Sources
    authors = models.ManyToManyField(Author, verbose_name=_('Authors'))
    source = models.ForeignKey(Source, blank=True, null=True, verbose_name=_('Source'))
    interviewees = models.ManyToManyField(Interviewee, verbose_name=_('Interviewees'))

    category = models.ForeignKey(Category, verbose_name=_('Category'))

    # Main Photo
    photo = models.ForeignKey(Photo, blank=True, null=True, verbose_name=_('Photo'))

    objects = RelatedManager()


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
        q = self.question_set.all().order_by('submit_date').exclude(pk__in=[ q['id'] for q in self.question_set.filter(answer__pk__isnull=False).values('id') ])
        return q

    def get_interviewees(self, user=None):
        if not user:
            from ella.core.middleware import get_current_request
            request = get_current_request()
            user = request.user
        if not hasattr(self, '_interviewees'):
            if not user.is_authenticated() or not self.can_reply():
                self._interviewees = []
            else:
                # TODO: filter only those interviewees that can be replying now (permission-wise)
                self._interviewees = get_cached_list(Interviewee, interview__pk=self.pk)
        return self._interviewees

    def get_photo(self):
        if not hasattr(self, '_photo'):
            try:
                self._photo = get_cached_object(Photo, pk=self.photo_id)
            except Photo.DoesNotExist:
                self._photo = None
        return self._photo

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

    def full_url(self):
        from django.utils.safestring import mark_safe
        absolute_url = self.get_absolute_url()
        if absolute_url:
            return mark_safe('<a href="%s">url</a>' % absolute_url)
        return 'no url'
    full_url.allow_tags = True


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
    ip_address = models.IPAddressField(_('ip address'), blank=True, null=True)

    # comment metadata
    submit_date = models.DateTimeField(_('date/time submitted'), default=datetime.now, editable=True)
    is_public = models.BooleanField(_('is public'), default=True)

    @property
    def author(self):
        if self.user_id():
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
        ordering = ('-submit_date',)
        verbose_name = _('Question')
        verbose_name_plural = _('Questions')


class Answer(models.Model):
    question = models.ForeignKey(Question)
    interviewee = models.ForeignKey(Interviewee)

    submit_date = models.DateTimeField(_('date/time submitted'), default=datetime.now)
    content = models.TextField(_('Answer text'))

    class Meta:
        ordering = ('-submit_date',)
        verbose_name = _('Answer')
        verbose_name_plural = _('Answer')

# initialization
from ella.comments import register
del register

