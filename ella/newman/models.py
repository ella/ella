from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

from ella.core.cache.utils import CachedForeignKey

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


# FIXME: maybe other solution than DB for help - need translations for this?
class AdminHelpItem(models.Model):
    """Help for ella administrators, that extends django help_text functionality."""

    ct = CachedForeignKey(ContentType, verbose_name=_('Model'))
    field = models.CharField(_('Field'), max_length=64, blank=True)
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

