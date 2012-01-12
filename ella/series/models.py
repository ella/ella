from datetime import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _

from ella.core.models import Publishable
from ella.core.cache.utils import CachedForeignKey, get_cached_list, get_cached_object
from ella.core.models import Publishable


class Serie(Publishable):
    hide_newer_parts = models.BooleanField(_('Hide newer parts'), default=False)
    started = models.DateField(_('Started'))
    finished = models.DateField(_('Finished'), null=True, blank=True)
    text = models.TextField(_('Text'))

    def parts_count(self):
        return len(self.parts)
    parts_count.short_description = _('Parts')

    @property
    def parts(self):
        return get_cached_list(SeriePart, serie=self, publishable__publish_from__lte=datetime.now())

    def is_active(self):
        today = datetime.date.today()
        return today > self.started and (self.finished is None or today < self.finished)
    is_active.short_description = _('Active')
    is_active.boolean = True

    def get_text(self):
        return self.text

    def __unicode__(self):
        return u"%s" % self.title

    class Meta:
        verbose_name = _('Serie')
        verbose_name_plural = _('Series')


class SeriePartManager(models.Manager):

    def get_serieparts_for_current_part(self, current_part):
        """  Return all parts for given part """
        kwargs = {'serie': current_part.serie}
        # Shall I hide newer parts?
        if current_part.serie.hide_newer_parts:
            kwargs['publishable__publish_from__lte'] = current_part.publishable.publish_from
        else:
            kwargs['publishable__publish_from__lte'] = datetime.now()

        return get_cached_list(SeriePart, **kwargs)

    def get_part_for_publishable(self, publishable):
        """ Return serie part for publishable """
        return get_cached_object(SeriePart, publishable = publishable)


class SeriePart(models.Model):

    serie = CachedForeignKey(Serie, verbose_name=_('Serie'))
    publishable = CachedForeignKey(Publishable, unique=True)
    part_no = models.PositiveSmallIntegerField(_('Part no.'), default=1, editable=False)

    objects = SeriePartManager()

    @property
    def target(self):
        return self.publishable.target

    def published(self):
        return self.publishable.publish_from

    def __unicode__(self):
        return u"%s %s: %s" % (self.publishable.target, _('in serie'), self.serie)

    class Meta:
        ordering = ('serie','publishable__publish_from',)
        verbose_name=_('Serie part')
        verbose_name_plural=_('Serie parts')
