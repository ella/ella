from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User, Group

from ella.core.cache.utils import CachedForeignKey
from django.conf import settings

class DevMessage(models.Model):
    """Development news for ella administrators."""

    title = models.CharField(_('Title'), max_length=255)
    slug = models.SlugField(_('Slug'), max_length=32)
    summary = models.TextField(_('Summary'))
    details = models.TextField(_('Detail'), blank=True)
    version = models.CharField(_('Version'), max_length=32)

    author = models.ForeignKey(User, editable=False)
    ts = models.DateTimeField(editable=False, auto_now_add=True)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('Development message')
        verbose_name_plural = _('Development messages')
        ordering = ('-ts',)
        unique_together = (('slug', 'ts',),)


class AdminHelpItem(models.Model):
    """Help for ella administrators, that extends django help_text functionality."""

    ct = CachedForeignKey(ContentType, verbose_name=_('Model'))
    field = models.CharField(_('Field'), max_length=64, blank=True)
    lang = models.CharField(_('Language'), max_length=5, choices=settings.LANGUAGES)
    short = models.CharField(_('Short help'), max_length=255)
    long = models.TextField(_('Full message'), blank=True)

    def __unicode__(self):
        if self.field:
            return u"%s: %s" % (self.ct, self.field)
        return u"%s: %s" % (self.ct, _('General'))

    class Meta:
        verbose_name = _('Help item')
        verbose_name_plural = _('Help items')
        ordering = ('ct', 'field',)
        unique_together = (('ct', 'field',),)


class AdminUserDraft(models.Model):
    """Here is auto-saved objects and user templates."""

    ct = CachedForeignKey(ContentType, verbose_name=_('Model'))
    user = CachedForeignKey(User, verbose_name=_('User'))
    data = models.TextField(_('Data')) # TODO: JSONField

    # If it's template, some info about it
    title = models.CharField(_('Title'), max_length=64, blank=True)
    slug = models.SlugField(_('Slug'), max_length=64, blank=True)

    is_template = models.BooleanField(_('Is template'), default=False)
    ts = models.DateTimeField(editable=False, auto_now_add=True)

    def __unicode__(self):
        if self.is_template:
            return self.title
        return "Autosaved %s (%s)" % (self.ct, self.ts)

    class Meta:
        verbose_name = _('Draft item')
        verbose_name_plural = _('Draft items')


class AdminSetting(models.Model):
    """Custom settings for newman users/groups"""

    user = CachedForeignKey(User, verbose_name=_('User'), null=True, blank=True)
    group = CachedForeignKey(Group, verbose_name=_('Group'), null=True, blank=True)
    var = models.SlugField(_('Variable'), max_length=64)
    val = models.TextField(_('Value')) # TODO: JSONField with validation...

    def __unicode__(self):
        return u"%s: %s for %s" % (self.var, self.val, self.user)

    class Meta:
        unique_together = (('user','var',),('group', 'var',),)
        verbose_name = _('Admin user setting')
        verbose_name_plural = _('Admin user settings')


class AdminGroupFav(models.Model):
    """Admin favorite items per group (presets)."""

    ct = CachedForeignKey(ContentType, verbose_name=_('Model'))
    group = CachedForeignKey(Group, verbose_name=_('Group'))
    ordering = models.PositiveSmallIntegerField(_('Ordering'))

    def __unicode__(self):
        return "%s - %s" % (self.group, self.ct)

    class Meta:
        unique_together = (('ct', 'group',),)
        ordering = ('ordering',)
        verbose_name = _('Group fav item')
        verbose_name_plural = _('Group fav items')


class AdminUserFav(models.Model):
    """Admin favorite items per user."""

    ct = CachedForeignKey(ContentType, verbose_name=_('Model'))
    user = CachedForeignKey(User, verbose_name=_('User'))
    ordering = models.PositiveSmallIntegerField(_('Ordering'))

    def __unicode__(self):
        return "%s - %s" % (self.user, self.ct)

    class Meta:
        unique_together = (('ct', 'user',),)
        ordering = ('ordering',)
        verbose_name = _('User fav item')
        verbose_name_plural = _('User fav items')
