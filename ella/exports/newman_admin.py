from django.utils.translation import ugettext_lazy as _
from django.forms import models as modelforms
from django.forms.fields import DateTimeField, ChoiceField, IntegerField, HiddenInput
from django.core import signals as core_signals

from ella import newman
from ella.newman import options, fields, widgets, config
from ella.exports import models


class ExportPositionInlineAdmin(newman.NewmanTabularInline):
    model = models.ExportPosition
    extra = 1

class ExportAdmin(newman.NewmanModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    suggest_fields = {
        'category': ('__unicode__', 'title', 'slug',),
    }

class ExportMetaAdmin(newman.NewmanModelAdmin):
    inlines = (ExportPositionInlineAdmin,)
    #raw_id_fields = ('photo',)
    suggest_fields = {
        'publishable': ('__unicode__', 'title', 'slug',),
        'photo': ('__unicode__', 'title', 'slug',)
    }

class HiddenIntegerField(IntegerField):
    widget = HiddenInput

class MetaInlineForm(modelforms.ModelForm):
    position_id = HiddenIntegerField(required=False)
    position_from =  DateTimeField(label=_('Valid From'), widget=widgets.DateTimeWidget)
    position_to =  DateTimeField(label=_('Valid To'), widget=widgets.DateTimeWidget)
    export =  modelforms.ModelChoiceField(models.Export.objects.all(), label=_('Export'))
    _export_stack = dict()

    def __init__(self, *args, **kwargs):
        super(MetaInlineForm, self).__init__(*args, **kwargs)
        core_signals.request_finished.connect(receiver=MetaInlineForm.reset_export_enumerator)
        existing_object = False
        new_object = False
        id_initial = None
        from_initial = to_initial = ''
        export_initial = None
        export_qs = models.Export.objects.all()
        if 'instance' in kwargs and 'data' not in kwargs:
            existing_object = True
            instance = kwargs['instance']
            if instance:
                id_initial, from_initial, to_initial, export_initial = self.get_initial_data(instance)
        elif 'data' not in kwargs:
            new_object = True

        self.assign_init_field(
            'position_id', 
            HiddenIntegerField(initial=id_initial, label=u'', required=False)
        )
        self.assign_init_field(
            'position_from', 
            DateTimeField(initial=from_initial, label=_('Valid From'), widget=widgets.DateTimeWidget)
        )
        self.assign_init_field(
            'position_to', 
            DateTimeField(initial=to_initial, label=_('Valid To'), widget=widgets.DateTimeWidget)
        )
        self.assign_init_field(
            'export', 
            modelforms.ModelChoiceField(export_qs, initial=export_initial, label=_('Export'), show_hidden_initial=True)
        )

    def assign_init_field(self, field_name, value):
        self.fields[field_name] = self.base_fields[field_name] = value

    def get_initial_data(self, instance):
        " @return tuple (visible_from, visible_to, export_initial) "
        positions = models.ExportPosition.objects.filter(object=instance)
        if not positions:
            return ('', '', None)
        pcount = positions.count()
        if pcount > 1 and not MetaInlineForm._export_stack.get(instance, False):
            MetaInlineForm._export_stack[instance] = list()
            map( lambda p: MetaInlineForm._export_stack[instance].insert(0, p), positions )
        if pcount == 1:
            pos = positions[0]
        elif pcount > 1:
            pos = MetaInlineForm._export_stack[instance].pop()
        out = (pos.pk, pos.visible_from, pos.visible_to, pos.export.pk)
        return out

    @staticmethod
    def reset_export_enumerator(*args, **kwargs):
        " Clears _export_stack at the end of HTTP request. "
        core_signals.request_finished.disconnect(receiver=MetaInlineForm.reset_export_enumerator)
        MetaInlineForm._export_stack.clear()

    def get_date_field_key(self, field):
        return '%s-%s' % (self.prefix, field)

    def clean(self):
        """
        if not self.is_valid() or not self.cleaned_data or not self.instance:
            return self.cleaned_data
        """
        self.cleaned_data['position_id'] = self.data[self.get_date_field_key('position_id')]
        self.cleaned_data['position_from'] = self.data[self.get_date_field_key('position_from')]
        self.cleaned_data['position_to'] = self.data[self.get_date_field_key('position_to')]
        self.cleaned_data['export'] = self.data[self.get_date_field_key('export')]
        return self.cleaned_data

    def save(self, commit=True):
        out = super(MetaInlineForm, self).save(commit=commit)

        def save_them():
            export = models.Export.objects.get(pk=int(self.cleaned_data['export']))
            positions = models.ExportPosition.objects.filter(
                object=self.instance, 
                export=export
            )
            if not self.cleaned_data['position_id']:
                position = models.ExportPosition(
                    object=self.instance, 
                )
            else:
                pos_id = int(self.cleaned_data['position_id'])
                position = models.ExportPosition.objects.get(pk=pos_id)
            position.export = export
            position.visible_from = self.cleaned_data['position_from']
            position.visible_to = self.cleaned_data['position_to']
            position.save()

        if commit:
            save_them()
        else:
            save_m2m = getattr(self, 'save_m2m', None)
            def save_all():
                if save_m2m:
                    save_m2m()
                save_them()
            self.save_m2m = save_all
        return out

class ExportMetaInline(newman.NewmanStackedInline):
    form = MetaInlineForm
    model = models.ExportMeta
    suggest_fields = {'photo': ('__unicode__', 'title', 'slug',)}
    extra = 1


newman.site.register(models.Export, ExportAdmin)
newman.site.register(models.ExportPosition)
newman.site.register(models.ExportMeta, ExportMetaAdmin)

# Register ExportMetaInline in standard PublishableAdmin
newman.site.append_inline(config.TAGGED_MODELS, ExportMetaInline)
