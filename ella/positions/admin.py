from django.contrib import admin

from ella.positions.models import Position

class PositionOptions(admin.ModelAdmin):
    list_display = ('name', 'category', 'box_type', 'is_active', 'is_filled', 'show_title',)
    list_filter = ('category', 'name', 'active_from', 'active_till',)
    search_fields = ('box_type', 'text',)

admin.site.register(Position, PositionOptions)

