from django.db import models, IntegrityError
from django.utils.translation import ugettext_lazy as _

from ella.core.models import Publishable, Category
from ella.photos.models import Photo
from ella.exports.managers import ExportManager


class Export(models.Model):
    " Export group. "
    #category = models.ForeignKey(Category, verbose_name=_('Category'))
    name = models.CharField(_('Name'), max_length=64)
    objects = ExportManager()

    def __unicode__(self):
        return u'%s: %s' % (unicode(self._meta.verbose_name), self.name)

    class Meta:
        unique_together = ('name',)
        verbose_name = _('Export')
        verbose_name_plural = _('Exports')


class ExportMeta(models.Model):
    """
    Redefine title, photo etc. for exported object
    """

    publishable = models.ForeignKey(Publishable, verbose_name=_('Publishable object'))
    title = models.CharField(_('Title'), max_length=64, blank=True)
    photo = models.ForeignKey(Photo, verbose_name=_('Photo'), blank=True, null=True)
    description = models.TextField(_('Description'), blank=True)

    def __unicode__(self):
        return u"%s: %s" % (_('Redefined export'), self.publishable)

    def save(self, force_insert=False, force_update=False):
        if not self.title and not self.photo and not self.description:
            raise IntegrityError
        super(ExportMeta, self).save(force_insert, force_update)

    class Meta:
        verbose_name = _('Export meta')
        verbose_name_plural = _('Export metas')


class ExportPosition(models.Model):
    " Defines visibility of ExportMeta object. "
    visible_from = models.DateTimeField()
    visible_to = models.DateTimeField()
    object = models.ForeignKey(ExportMeta, verbose_name=_('Export meta'))
    export = models.ForeignKey(Export, verbose_name=_('Export'))

    class Meta:
        verbose_name = _('Export Position')
        verbose_name_plural = _('Export Positions')

# EOF
