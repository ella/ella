from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.conf import settings
from django.template import Template

from ella.core.models import Category
from ella.core.box import Box
from ella.core.cache import get_cached_object

class PositionManager(models.Manager):
    def get_active_position(self, category, name, nofallback=False):
        """
        Get active position for given position name.

        params:
            category - Category model to look for
            name - name of the position
            nofallback - if True than do not fall back to parent
                        category if active position is not found for category
        """
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
                category = category.get_tree_parent()

                # we reached the top and still haven't found the position - raise
                if category is None:
                    raise

class Position(models.Model):
    " Represents a position on a page belonging to a certain category. "
    category = models.ForeignKey(Category, verbose_name=_('Category'))
    name = models.CharField(_('Name'), max_length=200)

    target_ct = models.ForeignKey(ContentType, verbose_name=_('Target content type'), null=True, blank=True)
    target_id = models.PositiveIntegerField(_('Target id'), null=True, blank=True)

    @property
    def target(self):
        if not hasattr(self, '_target'):
            try:
                target_ct = get_cached_object(ContentType, pk=self.target_ct_id)
                self._target = get_cached_object(target_ct, pk=self.target_id)
            except ObjectDoesNotExist:
                return None
        return self._target

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
        " Delegate the boxing. "
        obj = self.target
        if hasattr(obj, 'Box'):
            return obj.Box(box_type, nodelist)
        return Box(obj, box_type, nodelist)

    def render(self, context, nodelist, box_type):
        " Render the position. "
        if not self.target:
            return Template(self.text).render(context)

        if self.box_type:
            box_type = self.box_type
        if self.text:
            nodelist = Template(self.text).nodelist

        b = self.Box(box_type, nodelist)
        b.prepare(context)
        return b.render()

    def __unicode__(self):
        return '%s:%s' % (self.category, self.name)


# initialization
from ella.positions import register
del register

