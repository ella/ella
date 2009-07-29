from django.db import models, IntegrityError
from django.utils.translation import ugettext_lazy as _

from ella.core.models import Publishable
from ella.photos.models import Photo

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

