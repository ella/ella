from datetime import datetime

from django.db import models, transaction
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _, ugettext

from ella.core.cache import get_cached_object


class DbTemplate(models.Model):
    name = models.CharField(_('Name'), maxlength=200, db_index=True)
    site = models.ForeignKey(Site)
    description = models.CharField(_('Description'), maxlength=500, blank=True)
    extends = models.CharField(_('Base template'), maxlength=200)

    def get_text(self):
        text = u'{%% extends "%s" %%}\n\n' % self.extends

        for block in self.templateblock_set.filter(
                Q(active_from__isnull=True) | Q(active_from__lte=datetime.now()),
                Q(active_till__isnull=True) | Q(active_till__gt=datetime.now())
):
            text += '{%% block %s %%}\n' % block.name
            if block.box_type and block.target:
                text += '{%% box %s for %s.%s with id %s %%}\n' % (
                        block.box_type,
                        block.target_ct.app_label,
                        block.target_ct.model,
                        block.target_id
)
            text += block.text + '\n'
            if block.box_type and block.target:
                text += '{% endbox %}\n'
            text += '{% endblock %}\n\n'

        comment =  u'{% comment %}\n'
        comment += u'name: %s\n' % self.name
        comment += u'site: %s\n' % self.site
        comment += u'description: %s\n' % self.description
        comment += u'{% endcomment %}\n\n'
        text += comment

        return text

    class Meta:
        ordering = ('name',)
        unique_together = (('site', 'name'),)
        verbose_name = _('Template')
        verbose_name_plural = _('Templates')

    def __unicode__(self):
        return '%s <- %s' % (self.name, self.extends)


class TemplateBlock(models.Model):
    template = models.ForeignKey(DbTemplate)
    name = models.CharField(_('Name'), maxlength=200)
    box_type = models.CharField(_('Box type'), maxlength=200, blank=True)
    target_ct = models.ForeignKey(ContentType, null=True, blank=True)
    target_id = models.IntegerField(null=True, blank=True)
    active_from = models.DateTimeField(_('Block active from'), default=datetime.now, null=True, blank=True)
    active_till = models.DateTimeField(_('Block active till'), null=True, blank=True)

    text = models.TextField(_('Definition'), blank=True)

    @property
    def target(self):
        if not self.target_id or not self.target_ct:
            return None
        if not hasattr(self, '_target'):
            self._target = get_cached_object(self.target_ct, pk=self.target_id)
        return self._target

    class Meta:
        verbose_name = _('Teplate block')
        verbose_name_plural = _('Teplate blocks')
        unique_together = (('template', 'name',),)


# initialization
from ella.db_templates import register
del register

