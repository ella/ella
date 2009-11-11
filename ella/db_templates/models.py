from datetime import datetime
import re

from django.db import models
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.template import Template
from django.template.loader_tags import ExtendsNode, BlockNode

from ella.core.cache import CachedGenericForeignKey
from ella.core.templatetags.core import BoxNode


def get_blocks(block_list):
    blocks = []

    # TODO: source should not be extracted via regexp,
    # or this regexp should respect other values than {% %}
    re_block = re.compile(r'{%\s+block\s([^\s]+)\s+%}(.*?){%\s+endblock\s+%}', re.S)

    for i, node in enumerate(block_list):
        if not isinstance(node, BlockNode):
            continue

        source_start = node.source[1][0]
        if i+1 == len(block_list):
            source_end = len(node.source[0].source)
        else:
            source_end = block_list[i+1].source[1][0]
        # TODO: ugly
        block_source = re_block.findall(node.source[0].source[source_start:source_end])[0][1]

        blocks.append({
                'name': node.name,
                'node': node,
                'source': block_source
            })

    return blocks


class InvalidTemplate(Exception):
    pass

class DbTemplateManager(models.Manager):
    def create_from_string(self, template_string, name):
        site = settings.SITE_ID
        description = 'some db template'

        compiled_template = Template(template_string, name=name)

        if not len(compiled_template.nodelist):
            raise InvalidTemplate, 'template without nodes'
        if not isinstance(compiled_template.nodelist[0], ExtendsNode):
            raise InvalidTemplate, 'template without extends'

        re_description = re.compile('{%\s+comment\s+%}.*?description: (.*?){%\s+endcomment\s+%}', re.S)
        found = re_description.findall(template_string)
        if len(found):
            description = found[0].strip()

        extends = compiled_template.nodelist[0].parent_name
        blocks = get_blocks(compiled_template.nodelist[0].nodelist)

        db_template = DbTemplate(name=name, site_id=site, description=description, extends=extends)
        db_template.save()

        for b in blocks:
            TemplateBlock.objects.create_from_string(parent_template=db_template, template_string=b['source'], name=b['name'])

        return db_template


class DbTemplate(models.Model):
    name = models.CharField(_('Name'), max_length=200, db_index=True)
    site = models.ForeignKey(Site)
    description = models.CharField(_('Description'), max_length=500, blank=True)
    extends = models.CharField(_('Base template'), max_length=200)

    objects = DbTemplateManager()

    def get_text(self):
        text = [ u'{%% extends "%s" %%}' % self.extends, '' ]

        now = datetime.now()
        filter = (
                Q(active_from__isnull=True) | Q(active_from__lte=now),
                Q(active_till__isnull=True) | Q(active_till__gt=now),
            )
        for block in self.templateblock_set.filter(*filter):
            text.append('{%% block %s %%}\n%s\n{%% endblock %%}\n' % (block.name, block.get_text()))

        text.append(self.get_meta())

        return '\n'.join(text)

    def get_meta(self):
        meta = (
                u'{% comment %}',
                u'name: %s' % self.name,
                u'site: %s' % self.site,
                u'description: %s' % self.description,
                u'{% endcomment %}',
                '',
            )

        return '\n'.join(meta)

    class Meta:
        ordering = ('name',)
        unique_together = (('site', 'name'),)
        verbose_name = _('Template')
        verbose_name_plural = _('Templates')

    def __unicode__(self):
        return '%s' % self.name


class TemplateBlockManager(models.Manager):
    def create_from_string(self, parent_template, template_string, name):
        template_block = TemplateBlock(template=parent_template, name=name, text=template_string)

        node = Template(template_string.strip(), name=name, origin=parent_template.name)
        if len(node.nodelist) and isinstance(node.nodelist[0], BoxNode):
            box = node.nodelist[0]
            if box.lookup[0] in ('id', 'pk'):
                box_type = box.box_type
                target_ct = ContentType.objects.get_for_model(box.model)
                target_id = box.lookup[1]

                # TODO: params is compiled template - so it must not be TextNode
                # but we dont't want that ugly regexp here
                source = box.nodelist[0].source
                re_box = re.compile(r'{%\s+box\s[^%]+\s+%}(.*?){%\s+endbox\s+%}', re.S)
                params = re_box.findall(source[0].source)[0]

                template_block = TemplateBlock(
                        name=name, template=parent_template,
                        target_ct=target_ct, target_id=target_id,
                        box_type=box_type, text=params
                    )

        template_block.save()
        return template_block

class TemplateBlock(models.Model):
    template = models.ForeignKey(DbTemplate)
    name = models.CharField(_('Name'), max_length=200)
    box_type = models.CharField(_('Box type'), max_length=200, blank=True)
    target_ct = models.ForeignKey(ContentType, null=True, blank=True)
    target_id = models.IntegerField(null=True, blank=True)
    active_from = models.DateTimeField(_('Block active from'), null=True, blank=True)
    active_till = models.DateTimeField(_('Block active till'), null=True, blank=True)

    text = models.TextField(_('Definition'), blank=True)

    objects = TemplateBlockManager()

    target = CachedGenericForeignKey(ct_field="target_ct", fk_field="target_id")

    def get_text(self):
        text = []

        if self.box_type and self.target:
            text.append('{%% box %s for %s.%s with id %s %%}' % (
                    self.box_type,
                    self.target_ct.app_label,
                    self.target_ct.model,
                    self.target_id
                ))

        text.append(self.text.strip())

        if self.box_type and self.target:
            text.append('{% endbox %}')

        return '\n'.join(text)

    class Meta:
        verbose_name = _('Template block')
        verbose_name_plural = _('Template blocks')
        # unique_together = (('template', 'name',),)
        unique_together = (('template', 'name', 'active_from', 'active_till',),)

    def __unicode__(self):
        return '%s' % self.name

