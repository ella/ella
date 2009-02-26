from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from ella.core.cache.utils import CachedGenericForeignKey

class License(models.Model):

    ct = models.ForeignKey(ContentType, verbose_name=_('Content type'))
    obj_id = models.PositiveIntegerField(_('Object ID'))
    target = CachedGenericForeignKey('ct', 'obj_id')

    max_applications = models.PositiveIntegerField(_('Max applications'))
    applications = models.PositiveIntegerField(editable=False, default=0)

    def __unicode__(self):
        return u'License for %s' % self.target

    @property
    def applicable(self):
        return self.applications < self.max_applications

    class Meta:
        unique_together = (('ct', 'obj_id',),)
        verbose_name = _('License')
        verbose_name_plural = _('Licenses')
