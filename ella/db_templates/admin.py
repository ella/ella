from django.contrib import admin
from django.newforms.models import InlineFormset
from django.newforms.forms import ValidationError, NON_FIELD_ERRORS

from ella.db_templates.models import DbTemplate, TemplateBlock


class TemplateBlockFormset(InlineFormset):
    " Custom formset enabling us to supply custom validation. "

    @staticmethod
    def cmp_by_till(f, t):
        if f[1] is None:
            return 1
        elif t[1] is None:
            return -1
        else:
            return cmp(f[1], t[1])

    def clean(self):
        " Validate that the template's activity don't overlap. "
        if not self.cleaned_data:
            return self.cleaned_data

        # check that active_till datetime is greather then active_from
        validation_error = None
        for i, data in enumerate(self.cleaned_data):
            # both datetimes entered
            if data['active_from'] and data['active_till']:
                if data['active_from'] > data['active_till']:
                    validation_error = ValidationError(ugettext('Block active till must be greather then Block active from') % data)
                    self.forms[i]._errors['active_till'] = validation_error.messages
        if validation_error:
            raise ValidationError(ugettext('Invalid datetime interval. Block active till must be greather then Block active from') % data)

        # dictionary of blocks with tuples (active from, active till)
        items = {}
        for item in self.cleaned_data:
            if not items.has_key(item['name']):
                items[item['name']] = [(item['active_from'], item['active_till'])]
            else:
                items[item['name']].append((item['active_from'], item['active_till']))

        # check that intervals are not in colision
        errors = []
        error_message = 'Block active intervals are in colision on %s. Specified interval stops at %s and next interval started at %s.'
        for name, intervals in items.items():
            if len(intervals) > 1:
                intervals.sort(self.cmp_by_till)
                for i in xrange(len(intervals)-1):
                    try:
                        # exact covering allwoved (00:00:00 to 00:00:00)
                        if intervals[i][1] > intervals[i+1][0]:
                            errors.append(error_message % (name, intervals[i][1], intervals[i+1][0]))
                    except TypeError:
                        errors.append(error_message % (name, 'Infinite', intervals[i+1][0]))
        if errors:
            raise ValidationError, errors

        return self.cleaned_data

class TemplateBlockInlineOptions(admin.TabularInline):
    model = TemplateBlock
    extra = 3
    fieldsets = ((None, {'fields' : ('name', 'box_type', 'target_ct', 'target_id', 'active_from', 'active_till', 'text',)}),)
    formset = TemplateBlockFormset

class DbTemplateOptions(admin.ModelAdmin):
    ordering = ('description',)
    inlines = (TemplateBlockInlineOptions,)
    list_display = ('description', 'site', 'extends', 'name')
    list_filter = ('site',)

admin.site.register(DbTemplate, DbTemplateOptions)

