import operator

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from ella.core.cache.utils import CachedGenericForeignKey

class LicenseManager(models.Manager):
    def _get_queryset_of_unapplicables(self, model):
        ct = ContentType.objects.get_for_model(model)
        return License.objects.filter(ct=ct, applications__gte=models.F('max_applications')).values('obj_id')

    def unapplicable_for_model(self, model):
        return [u['obj_id'] for u in self._get_queryset_of_unapplicables(model)]

    def filter_queryset(self, queryset):
        qset = queryset.exclude(pk__in=self._get_queryset_of_unapplicables(queryset.model))
        return qset

    def _reflect_changed_dependencies(self, deps, delta):
        if not deps:
            return
        get_condition = lambda dep: models.Q(ct=dep.target_ct, obj_id=dep.target_id)
        self.filter(reduce(operator.or_, map(get_condition, deps))).update(applications=models.F('applications')+delta)

    def reflect_added_dependencies(self, deps):
        self._reflect_changed_dependencies(deps, 1)

    def reflect_removed_dependencies(self, deps):
        self._reflect_changed_dependencies(deps, -1)

class License(models.Model):

    ct = models.ForeignKey(ContentType, verbose_name=_('Content type'))
    obj_id = models.PositiveIntegerField(_('Object ID'))
    target = CachedGenericForeignKey('ct', 'obj_id')

    max_applications = models.PositiveIntegerField(_('Max applications'))
    applications = models.PositiveIntegerField(editable=False, default=0)

    note = models.CharField(_('Note'), max_length=255, blank=True)

    objects = LicenseManager()

    def __unicode__(self):
        return _('License for %s') % self.target

    @property
    def applicable(self):
        return self.applications < self.max_applications

    class Meta:
        unique_together = (('ct', 'obj_id',),)
        verbose_name = _('License')
        verbose_name_plural = _('Licenses')
