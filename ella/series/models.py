from datetime import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _

from ella.core.models import Category, Placement
from ella.core.cache.utils import CachedForeignKey, get_cached_list, get_cached_object
from ella.db.models import Publishable
from ella.photos.models import Photo


class Serie(Publishable):

    title = models.CharField(_('Title'), max_length=96)
    slug = models.SlugField(_('Slug'), unique=True)
    perex = models.TextField(_('Perex'))
    description = models.TextField(_('Description'), blank=True)
    category = models.ForeignKey(Category, verbose_name=_('Category'))

    hide_newer_parts = models.BooleanField(_('Hide newer parts'), default=False)
    started = models.DateField(_('Started'))
    finished = models.DateField(_('Finished'), null=True, blank=True)

    # Main Photo to Article
    photo = models.ForeignKey(Photo, blank=True, null=True, verbose_name=_('Photo'))

    def get_text(self):
        return self.description

    def parts_count(self):
        return len(self.parts)
    parts_count.short_description = _('Parts')

    @property
    def parts(self):
        return get_cached_list(SeriePart, serie=self, placement__publish_from__lte=datetime.now())

    def is_active(self):
        today = datetime.date.today()
        return today > self.started and (self.finished is None or today < self.finished)
    is_active.short_description = _('Active')
    is_active.boolean = True

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('Serie')
        verbose_name_plural = _('Series')


class SeriePartManager(models.Manager):

    def get_serieparts_for_current_part(self, current_part):
        """  Return all parts for given part """
        kwargs = {'serie': current_part.serie}
        # Shall I hide newer parts?
        if current_part.serie.hide_newer_parts:
            kwargs['placement__publish_from__lte'] = current_part.placement.publish_from
        else:
            kwargs['placement__publish_from__lte'] = datetime.now()

        return get_cached_list(SeriePart, **kwargs)

    def get_part_for_placement(self, placement):
        """ Return serie part for placement """
        return get_cached_object(SeriePart, placement = placement)


class SeriePart(models.Model):

    serie = CachedForeignKey(Serie, verbose_name=_('Serie'))
    placement = CachedForeignKey(Placement, unique=True)
    part_no = models.PositiveSmallIntegerField(_('Part no.'), default=1, editable=False)

    objects = SeriePartManager()

    @property
    def target(self):
        return self.placement.target

    def published(self):
        return self.placement.publish_from

    def target_admin(self):
        return self.target
    target_admin.short_description = _('Target')

    def __unicode__(self):
        return u"%s %s: %s" % (self.target,_('in serie'),self.serie)

    class Meta:
        ordering = ('serie','placement__publish_from',)
        verbose_name=_('Serie part')
        verbose_name_plural=_('Serie parts')
