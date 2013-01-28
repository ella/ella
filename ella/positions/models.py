import logging

from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.db.models import Q
from django.template import Template, TemplateSyntaxError
from django.core.exceptions import ValidationError

from ella.core.box import Box
from ella.core.cache import cache_this, CachedGenericForeignKey, \
    CategoryForeignKey, ContentTypeForeignKey, get_cached_object
from ella.utils import timezone


log = logging.getLogger('ella.positions.models')


def get_position_key(self, category, name, nofallback=False):
    return 'positions:%d:%s:%s' % (
            category.pk, name, nofallback and '1' or '0'
    )


class PositionManager(models.Manager):
    @cache_this(get_position_key)
    def get_active_position(self, category, name, nofallback=False):
        """
        Get active position for given position name.

        params:
            category - Category model to look for
            name - name of the position
            nofallback - if True than do not fall back to parent
                        category if active position is not found for category
        """
        now = timezone.now()
        lookup = (Q(active_from__isnull=True) | Q(active_from__lte=now)) & \
                 (Q(active_till__isnull=True) | Q(active_till__gt=now))

        while True:
            try:
                return self.get(lookup, category=category, name=name,
                    disabled=False)
            except Position.DoesNotExist:
                # if nofallback was specified, do not look into parent categories
                if nofallback:
                    return False

                # traverse the category tree to the top otherwise
                category = category.tree_parent

                # we reached the top and still haven't found the position - return
                if category is None:
                    return False


def PositionBox(position, *args, **kwargs):
    " Delegate the boxing. "
    obj = position.target
    return getattr(position.target, 'box_class', Box)(obj, *args, **kwargs)


class Position(models.Model):
    """
    Represents a position -- a placeholder -- on a page belonging to a certain
    category.
    """
    box_class = staticmethod(PositionBox)

    name = models.CharField(_('Name'), max_length=200)
    category = CategoryForeignKey(verbose_name=_('Category'))

    target_ct = ContentTypeForeignKey(verbose_name=_('Target content type'),
        null=True, blank=True)
    target_id = models.PositiveIntegerField(_('Target id'), null=True, blank=True)
    target = CachedGenericForeignKey('target_ct', 'target_id')
    text = models.TextField(_('Definition'), blank=True)
    box_type = models.CharField(_('Box type'), max_length=200, blank=True)

    active_from = models.DateTimeField(_('Position active from'), null=True,
        blank=True)
    active_till = models.DateTimeField(_('Position active till'), null=True,
        blank=True)
    disabled = models.BooleanField(_('Disabled'), default=False)

    objects = PositionManager()

    class Meta:
        verbose_name = _('Position')
        verbose_name_plural = _('Positions')

    def clean(self):
        if not self.category or not self.name:
            return

        if self.target_ct:
            try:
                get_cached_object(self.target_ct, pk=self.target_id)
            except self.target_ct.model_class().DoesNotExist:
                raise ValidationError(_('This position doesn\'t point to a valid object.'))

        qset = Position.objects.filter(category=self.category, name=self.name)

        if self.pk:
            qset = qset.exclude(pk=self.pk)

        if self.active_from:
            qset = qset.exclude(active_till__lte=self.active_from)

        if self.active_till:
            qset = qset.exclude(active_from__gt=self.active_till)

        if qset.count():
            raise ValidationError(_('There already is a postion for %(cat)s named %(name)s fo this time.') % {'cat': self.category, 'name': self.name})

    def __unicode__(self):
        return u'%s:%s' % (self.category, self.name)

    def render(self, context, nodelist, box_type):
        " Render the position. "
        if not self.target:
            if self.target_ct:
                # broken Generic FK:
                log.warning('Broken target for position with pk %r', self.pk)
                return ''
            try:
                return Template(self.text, name="position-%s" % self.name).render(context)
            except TemplateSyntaxError:
                log.error('Broken definition for position with pk %r', self.pk)
                return ''

        if self.box_type:
            box_type = self.box_type
        if self.text:
            nodelist = Template('%s\n%s' % (nodelist.render({}), self.text),
                name="position-%s" % self.name).nodelist

        b = self.box_class(self, box_type, nodelist)
        return b.render(context)
