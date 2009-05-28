from ella import newman

from ella.positions.models import Position

class PositionOptions(newman.NewmanModelAdmin):
    list_display = ('name', 'category', 'box_type', 'is_active', 'is_filled', 'show_title', 'disabled',)
    list_filter = ('category', 'disabled', 'active_from', 'active_till',)
    search_fields = ('name', 'box_type', 'text', 'category__title',)

    suggest_fields = {'category': ('title', 'slug', 'tree_path',),}

newman.site.register(Position, PositionOptions)

