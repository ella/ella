from ella import newman

from ella.positions.models import Position

class PositionOptions(newman.NewmanModelAdmin):
    list_display = ('name', 'category', 'box_type', 'is_active', 'is_filled', 'show_title', 'disabled',)
#    list_filter = ('category', 'name', 'active_from', 'active_till',)
    search_fields = ('box_type', 'text',)

    suggest_fields = {'category': ('tree_path', 'title', 'slug',),}

newman.site.register(Position, PositionOptions)

