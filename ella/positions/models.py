from datetime import datetime

from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.conf import settings

from ella.core.models import Category


class PositionManager(models.Manager):
    def get_active_positions(self, **lookup):
        now = datetime.now()
        return self.filter(
                    Q(active_from__isnull=True) | Q(active_from__lte=now),
                    Q(active_till__isnull=True) | Q(active_till__gt=now),
                    **lookup
)

class Position(models.Model):
    category = models.ForeignKey(Category, verbose_name=_('Category'))
    name = models.CharField(_('Name'), max_length=200)

    target_ct = models.ForeignKey(ContentType, verbose_name=_('Target content type'), null=True, blank=True)
    target_id = models.PositiveIntegerField(_('Target id'), null=True, blank=True)
    target = generic.GenericForeignKey(ct_field="target_ct", fk_field="target_id")

    active_from = models.DateTimeField(_('Position active from'), null=True, blank=True)
    active_till = models.DateTimeField(_('Position active till'), null=True, blank=True)

    box_type = models.CharField(_('Box type'), max_length=200, blank=True)
    text = models.TextField(_('Definition'), blank=True)

    objects = PositionManager()

    def is_active(self):
        now = datetime.now()
        active_from = not self.active_from or self.active_from <= now
        active_till = not self.active_till or self.active_till > now
        return active_from and active_till
    is_active.short_description = _('Active')
    is_active.boolean = True

    def __unicode__(self):
        return '%s:%s' % (self.category, self.name)


# initialization
from ella.positions import register
del register

