from datetime import datetime
from django.contrib import admin
from django.utils.translation import ugettext, ugettext_lazy as _

from ella.ellaadmin.options import EllaAdminOptionsMixin
from ella.positions.models import Position

class PositionOptions(EllaAdminOptionsMixin, admin.ModelAdmin):
    def show_title(self):
        if not self.target:
            return '-- %s --' % ugettext('empty position')
        else:
            return u'%s [%s]' % (self.target.title, ugettext(self.target_ct.name),)
    show_title.short_description = _('Title')

    def is_filled(self):
        if self.target:
            return True
        else:
            return False
    is_filled.short_description = _('Filled')
    is_filled.boolean = True

    def is_active(self):
        if self.disabled:
            return False
        now = datetime.now()
        active_from = not self.active_from or self.active_from <= now
        active_till = not self.active_till or self.active_till > now
        return active_from and active_till
    is_active.short_description = _('Active')
    is_active.boolean = True

    list_display = ('name', 'category', 'box_type', 'is_active', 'is_filled', 'show_title', 'disabled',)
    list_filter = ('category', 'name', 'disabled', 'active_from', 'active_till',)
    search_fields = ('box_type', 'text',)

#    suggest_fields = {'category': ('tree_path', 'title', 'slug',),}

admin.site.register(Position, PositionOptions)

