import logging
from datetime import datetime

from django.utils.translation import ugettext_lazy as _, ugettext
from django.db import models
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.template import Template, TemplateSyntaxError

from ella.core.models import Category
from ella.core.box import Box
from ella.core.cache import CACHE_DELETER, cache_this, CachedGenericForeignKey


log = logging.getLogger('ella.positions.models')

def get_position_key(func, self, category, name, nofallback=False):
    return 'ella.positions.models.PositionManager.get_active_position:%d:%s:%s' % (
            category.pk, name, nofallback and '1' or '0'
    )
def invalidate_cache(key,  self, category, name, nofallback=False):
    CACHE_DELETER.register_test(Position, "category_id:%s;name:%s" % (category.pk, name) , key)

class PositionManager(models.Manager):
    @cache_this(get_position_key, invalidate_cache)
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
                return self.get(lookup, category=category, name=name, disabled=False)
            except Position.DoesNotExist:
                # if nofallback was specified, do not look into parent categories
                if nofallback:
                    raise

                # traverse the category tree to the top otherwise
                category = category.get_tree_parent()

                # we reached the top and still haven't found the position - raise
                if category is None:
                    raise

def PositionBox(position, *args, **kwargs):
    " Delegate the boxing. "
    obj = position.target
    return getattr(position.target, 'box_class', Box)(obj, *args, **kwargs)


class Position(models.Model):
    " Represents a position on a page belonging to a certain category. "
    box_class = staticmethod(PositionBox)

    category = models.ForeignKey(Category, verbose_name=_('Category'))
    name = models.CharField(_('Name'), max_length=200)

    target_ct = models.ForeignKey(ContentType, verbose_name=_('Target content type'), null=True, blank=True)
    target_id = models.PositiveIntegerField(_('Target id'), null=True, blank=True)

    target = CachedGenericForeignKey('target_ct', 'target_id')

    active_from = models.DateTimeField(_('Position active from'), null=True, blank=True)
    active_till = models.DateTimeField(_('Position active till'), null=True, blank=True)

    box_type = models.CharField(_('Box type'), max_length=200, blank=True)
    text = models.TextField(_('Definition'), blank=True)
    disabled = models.BooleanField(_('Disabled'), default=False)

    objects = PositionManager()

    def render(self, context, nodelist, box_type):
        " Render the position. "
        if not self.target:
            if self.target_ct:
                # broken Generic FK:
                log.warning('Broken target for position with pk %r', self.pk)
                return ''
            try:
                return Template(self.text, name="position-%s" % self.name).render(context)
            except TemplateSyntaxError, e:
                log.error('Broken definition for position with pk %r', self.pk)
                return ''

        if self.box_type:
            box_type = self.box_type
        if self.text:
            nodelist = Template('%s\n%s' % (nodelist.render({}), self.text), name="position-%s" % self.name).nodelist

        b = self.box_class(self, box_type, nodelist)
        b.prepare(context)
        return b.render()

    def __unicode__(self):
        return u'%s:%s' % (self.category, self.name)

    class Meta:
        verbose_name = _('Position')
        verbose_name_plural = _('Positions')
