from datetime import datetime

from django.db import models, transaction
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _, ugettext
from django.newforms.models import InlineFormset
from django.newforms.forms import ValidationError, NON_FIELD_ERRORS

from ella.core.cache import get_cached_object


class DbTemplate(models.Model):
    name = models.CharField(_('Name'), maxlength=200, db_index=True)
    site = models.ForeignKey(Site)
    description = models.CharField(_('Description'), maxlength=500, blank=True)
    extends = models.CharField(_('Base template'), maxlength=200)

    text = models.TextField(_('Definition'), editable=False)
    def get_text(self):
        text = u'{%% extends "%s" %%}' % self.extends
        for block in self.templateblock_set.all():
            text += '{%% block %s %%}' % block.name
            if block.box_type and block.target:
                text += '{%% box %s for %s.%s with id %s %%}' % (
                        block.box_type,
                        block.target_ct.app_label,
                        block.target_ct.model,
                        block.target_id
)
            text += block.text + '\n'
            if block.box_type and block.target:
                text += '{% endbox %}'
            text += '{% endblock %}'
        return text

    class Meta:
        ordering = ('name',)

    def save(self):
        self.text = self.get_text()
        super(DbTemplate, self).save()

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

    @transaction.commit_on_success
    def save(self):
        super(TemplateBlock, self).save()
        # regenerate the full text
        self.template.save()

    class Meta:
        verbose_name = _('Teplate block')
        verbose_name_plural = _('Teplate blocks')
        unique_together = (('template', 'name',),)

class TemplateBlockFormset(InlineFormset):

    @staticmethod
    def cmp_by_till(f, t):
        if f[1] is None:
            return 1
        elif t[1] is None:
            return -1
        else:
            return cmp(f[1], t[1])

    def clean(self):
        if not self.cleaned_data:
            return self.cleaned_data

        # temp
        from pprint import pprint
        #pprint(self.cleaned_data)

        # check that active_till datetime is greather then active_from
        validation_error = None
        for i in xrange(len(self.cleaned_data)):
            # both datetimes entered
            if self.cleaned_data[i]['active_from'] and self.cleaned_data[i]['active_till']:
                if self.cleaned_data[i]['active_from'] > self.cleaned_data[i]['active_till']:
                    validation_error = ValidationError(ugettext('Invalid datetime interval %(active_from)s - %(active_till)s. Block active till must be greather then Block active from' % self.cleaned_data[i]))
                    self.forms[i]._errors = {NON_FIELD_ERRORS: validation_error.messages}
        if validation_error:
            raise ValidationError(ugettext('grrr'))

         # dictionary of blocks with tuples (active from, active till)
        items = {}
        for item in self.cleaned_data:
            if not items.has_key(item['name']):
                items[item['name']] = [(item['active_from'], item['active_till'])]
            else:
                items[item['name']].append((item['active_from'], item['active_till']))

#        errors = []
#        for deltas in items.values():
#            #print "jedem %s\n" % deltas
#            if len(deltas) > 1:
#                deltas.sort(self.cmp_by_till)
#                pprint(deltas)
#                for i in xrange(len(deltas) - 1):
#                    print "\tpokus %d: %s vs %s\n" % (i, deltas[i][1],  deltas[i+1][0])
#                    td = deltas[i+1][0] - deltas[i][1]
#                    print "\t\tvysledek: %s\n" % td

#        raise ValidationError, 'Jebkymrdky a co ja? datum od je %s a datum do je %s' % (self.cleaned_data[0], self.cleaned_data[1])

class TemplateBlockInlineOptions(admin.TabularInline):
    model = TemplateBlock
    extra = 3
    fieldsets = ((None, {'fields' : ('name', 'box_type', 'target_ct', 'target_id', 'active_from', 'active_till', 'text',)}),)
    formset = TemplateBlockFormset

class DbTemplateOptions(admin.ModelAdmin):
    ordering = ('description',)
    inlines = (TemplateBlockInlineOptions,)
    list_display = ('description', 'site', 'extends', 'name')

admin.site.register(DbTemplate, DbTemplateOptions)
