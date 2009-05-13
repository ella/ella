import operator

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from ella.core.cache.utils import CachedGenericForeignKey
from ella.core.models import Dependency
from ella.newman.licenses import LICENSED_MODELS

class LicenseManager(models.Manager):
    def _get_queryset_of_unapplicables(self, model):
        ct = ContentType.objects.get_for_model(model)
        return License.objects.filter(ct=ct, applications__gte=models.F('max_applications'))

    def unapplicable_for_model(self, model):
        return [u['obj_id'] for u in self._get_queryset_of_unapplicables(model).values('obj_id')]
    
    def filter_queryset(self, queryset):
        qset = queryset.exclude(pk__in=self._get_queryset_of_unapplicables(queryset.model))
        return qset

    def reflect_changed_dependencies(self, before, after):
        """ Update current applications if target model is licensed. """
        get_target = lambda dep: (dep.target_ct, dep.target_id)
        get_condition = lambda tgt: models.Q(ct=tgt[0], pk=tgt[1])

        b = set(map(get_target, before))
        a = set(map(get_target, after))
        add = a - b
        delete = b - a

        if add:
            self.filter(reduce(operator.or_, map(get_condition, add))).update(applications=models.F('applications')+1)

        if delete:
            self.filter(reduce(operator.or_, map(get_condition, delete))).update(applications=models.F('applications')-1)

class License(models.Model):

    ct = models.ForeignKey(ContentType, verbose_name=_('Content type'))
    obj_id = models.PositiveIntegerField(_('Object ID'))
    target = CachedGenericForeignKey('ct', 'obj_id')

    max_applications = models.PositiveIntegerField(_('Max applications'))
    applications = models.PositiveIntegerField(editable=False, default=0)

    objects = LicenseManager()

    def __unicode__(self):
        return u'License for %s' % self.target

    @property
    def applicable(self):
        return self.applications < self.max_applications

    class Meta:
        unique_together = (('ct', 'obj_id',),)
        verbose_name = _('License')
        verbose_name_plural = _('Licenses')
