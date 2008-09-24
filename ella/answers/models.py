# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext as _
from django.utils.text import wrap
from django.contrib.auth.models import User

from ella.ellaadmin.utils import admin_url


class Question(models.Model):
    text = models.CharField(_(u'Question'), max_length=200)
    specification = models.TextField(_(u'Specification'))
    nick = models.CharField(_('Nickname'), max_length=150)
    created = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField()

    def __unicode__(self):
        return self.text

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
        """
            Returns True whether answer is published by an expert otherwise False.
            Expert = self.authorized_user is member of specific user group.
        """
        if not self.authorized_user:
            return False
        if 'answers.can_answer_as_expert' in self.authorized_user.get_group_permissions():
            return True
        return False

    class Meta:
        ordering = ('-created',)
        permissions = (
            ('can_answer_as_expert', _('Can answer as an expert')),
)
