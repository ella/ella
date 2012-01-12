from datetime import datetime

from django.db import models
from django.utils.timesince import timesince
from django.utils.translation import ugettext_lazy as _

from ella.core.models import Publishable
from ella.core.cache import get_cached_list

class InfoBox(models.Model):
    """Defines embedable text model."""

    title = models.CharField(_('Title'), max_length=255)
    created = models.DateTimeField(_('Created'), default=datetime.now, editable=False)
    updated = models.DateTimeField(_('Updated'), blank=True, null=True)
    content = models.TextField(_('Content'))

    def __unicode__(self):
        return u"%s" % self.title

    class Meta:
        verbose_name = _('Info box')
        verbose_name_plural = _('Info boxes')


class Article(Publishable):
    """Defines article model."""
    upper_title = models.CharField(_('Upper title'), max_length=255, blank=True)
    created = models.DateTimeField(_('Created'), default=datetime.now, editable=False, db_index=True)
    updated = models.DateTimeField(_('Updated'), blank=True, null=True)

    content = models.TextField(_('Content'), default='')

    class Meta:
        verbose_name = _('Article')
        verbose_name_plural = _('Articles')

    def __unicode__(self):
        return self.title

    def article_age(self):
        """Returns time since article was created"""
        return timesince(self.created)
    article_age.short_description = _('Article Age')

    def get_text(self):
        return self.content


