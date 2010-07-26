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
        ordering = ('-created',)
        verbose_name = _('Info box')
        verbose_name_plural = _('Info boxes')


class Article(Publishable):
    """Defines article model."""
    upper_title = models.CharField(_('Upper title'), max_length=255, blank=True)
    created = models.DateTimeField(_('Created'), default=datetime.now, editable=False, db_index=True)
    updated = models.DateTimeField(_('Updated'), blank=True, null=True)

    @property
    def content(self):
        """Returns first item from ArticleContents linked to current article"""
        if not hasattr(self, '_contents'):
            self._contents = get_cached_list(ArticleContents, article=self)
        if self._contents:
            return self._contents[0]
        else:
            return None

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
        return self.content.content



class ArticleContents(models.Model):
    """Defines article's contents model.

    One article can have multiple contets. (1:N)"""
    article = models.ForeignKey(Article, verbose_name=_('Article'))
    title = models.CharField(_('Title'), max_length=200, blank=True)
    content = models.TextField(_('Content'))

    class Meta:
        verbose_name = _('Article content')
        verbose_name_plural = _('Article contents')
        #order_with_respect_to = 'article'

    def __unicode__(self):
        return self.title or unicode(self.article)

