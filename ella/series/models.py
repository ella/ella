from datetime import datetime
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from ella.core.models import Category
from ella.core.cache.utils import get_cached_object, get_cached_list
from ella.db.models import Publishable
from ella.core.box import Box


class Serie(models.Model, Publishable):

    title = models.CharField(_('Title'), max_length=96)
    slug = models.SlugField(_('Slug'), unique=True)
    perex = models.TextField(_('Perex'))
    description = models.TextField(_('Description'), blank=True)
    category = models.ForeignKey(Category, verbose_name=_('Category'))

    started = models.DateField(_('Started'))
    finished = models.DateField(_('Finished'), null=True, blank=True)

    @property
    def parts(self):
        return get_cached_list(SeriePart, serie=self)

    def is_active(self):
        today = datetime.date.today()
        return today > self.started and (self.finished is None or today < self.finished)
    is_active.short_description = _('Active')
    is_active.boolean = True

    def __unicode__(self):
        return u"%s" % self.title

    class Meta:
        verbose_name = _('Serie')
        verbose_name_plural = _('Series')


class SeriePart(models.Model):

    serie = models.ForeignKey(Serie, verbose_name=_('Serie'))
    target_ct = models.ForeignKey(ContentType)
    target_id = models.IntegerField()
    part_no = models.PositiveSmallIntegerField(_('Part no.'), default=1)

    @property
    def target(self):
        "Return target object via cache"
        if not hasattr(self, '_target'):
            self._target = get_cached_object(self.target_ct, pk=self.target_id)
        return self._target

    def __unicode__(self):
        return u"%s %s: %s" % (self.target,_('in serie'),self.serie)

    class Meta:
        unique_together=(('serie', 'target_ct', 'target_id',),)
        ordering = ('serie','part_no',)
        verbose_name=_('Serie part')
        verbose_name_plural=_('Serie parts')


