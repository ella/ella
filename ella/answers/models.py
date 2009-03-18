# -*- coding: utf-8 -*-
from datetime import timedelta, datetime

from django.db import models
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.sites.models import Site

from ella.ellaadmin.utils import admin_url
from ella.answers.fields import TimedeltaField

DEFAULT_TIMELIMIT = timedelta(14) # 14 days - used only when no QuestionGroup for Question is found

def get_default_timelimit():
    return datetime.now() + DEFAULT_TIMELIMIT

def is_expert_user(user):
    """
        Returns True whether answer is published by an expert otherwise False.
        Expert = self.authorized_user is member of specific user group.
    """
    if not user or isinstance(user, AnonymousUser):
        return False
    if 'answers.can_answer_as_expert' in user.get_group_permissions():
        return True
    return False

class Question(models.Model):
    text = models.CharField(_(u'Question'), max_length=200)
    specification = models.TextField(_(u'Specification'))
    nick = models.CharField(_('Nickname'), max_length=150)
    created = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField()
    timelimit = models.DateTimeField(default=get_default_timelimit())

    def __unicode__(self):
        return self.text

    @property
    def is_answerable(self):
        if not self.timelimit: # timelimit not set
            return True
        if datetime.now() < self.timelimit:
            return True
        return False

    @property
    def first_answer(self):
        if not self.pk:
            return None
        premium_answers = Answer.objects.filter(question=self, authorized_user__isnull=False).order_by('-created')
        if premium_answers:
            return premium_answers[0]
        answers = Answer.objects.filter(question=self).order_by('-created')
        if answers:
            return answers[0]
        return None

    class Meta:
        ordering = ('-created',)

class Answer(models.Model):
    text = models.TextField(_('Answer text'))
    nick = models.CharField(_('Nickname'), max_length=150) # odbornici budou udavat adresu atd.
    authorized_user = models.ForeignKey(User, verbose_name=_('Authorized user'), blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    question = models.ForeignKey(Question)
    is_hidden = models.BooleanField(_('Is hidden'), default=False)

    def __unicode__(self):
        return self.text

    def get_admin_url(self):
        return admin_url(self)

    def is_expert_response(self):
        return is_expert_user(self.authorized_user)

    class Meta:
        ordering = ('-created',)
        permissions = (
            ('can_answer_as_expert', _('Can answer as an expert')),
)

class QuestionGroup(models.Model):
    site = models.ForeignKey(Site)
    questions = models.ManyToManyField(Question)
    default_timelimit = TimedeltaField()

    def __unicode__(self):
        return 'Question Group for site %s' % self.site.name
