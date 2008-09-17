# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext as _
from django.utils.text import wrap


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
    created = models.DateTimeField(auto_now_add=True)
    question = models.ForeignKey(Question)
    is_hidden = models.BooleanField(_('Is hidden'), default=False)

    def __unicode__(self):
        return self.text

    class Meta:
        ordering = ('-created',)
