from datetime import datetime

from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.conf import settings
from django.template import Template

from ella.core.models import Category
from ella.core.box import Box


class PositionManager(models.Manager):
    def get_active_position(self, category, name, nofallback=False):
        now = datetime.now()
        lookup = (Q(active_from__isnull=True) | Q(active_from__lte=now)) & (Q(active_till__isnull=True) | Q(active_till__gt=now))
        while True:
            try:
                return self.get(lookup, category=category, name=name)
            except Position.DoesNotExist:
                # if nofallback was specified, do not look into parent categories
                if nofallback:
                    raise

                # traverse the category tree to the top otherwise
                elif category.tree_parent:
                    category = category.tree_parent

                # we reached the top and still haven't found the position - raise
                else:
                    raise

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

    def Box(self, box_type, nodelist):
        """Delegate the boxing"""
        obj = self.target

        if hasattr(obj, 'Box'):
            return obj.Box(box_type, nodelist)
        return Box(obj, box_type, nodelist)

    def render(self, context, nodelist, box_type=None):
        if self.target:
            if not box_type:
                box_type = self.box_type
            b = self.Box(box_type, nodelist)
            b.prepare(context)
            return b.render()
        return Template(self.text).render(context)

    def __unicode__(self):
        return '%s:%s' % (self.category, self.name)


# initialization
from ella.positions import register
del register

