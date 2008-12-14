from django.contrib import admin

from ella.ellaadmin.options import EllaAdminOptionsMixin
from ella.positions.models import Position

class PositionOptions(EllaAdminOptionsMixin, admin.ModelAdmin):
    list_display = ('name', 'category', 'box_type', 'is_active', 'is_filled', 'show_title', 'disabled',)
    list_filter = ('category', 'name', 'disabled', 'active_from', 'active_till',)
    search_fields = ('box_type', 'text',)

#    suggest_fields = {'category': ('tree_path', 'title', 'slug',),}

admin.site.register(Position, PositionOptions)

