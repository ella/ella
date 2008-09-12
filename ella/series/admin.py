from django.contrib import admin
from ella.series.models import Serie, SeriePart
from ella.ellaadmin.options import EllaAdminOptionsMixin

from ella.core.admin import PlacementInlineOptions
from ella.tagging.admin import TaggingInlineOptions

class SeriePartInlineAdmin(EllaAdminOptionsMixin, admin.TabularInline):
    model = SeriePart
    extra = 5


class SerieAdmin(EllaAdminOptionsMixin, admin.ModelAdmin):
    list_display = ('title', 'started', 'is_active')
    list_filter = ('started', 'finished',)
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'perex',)

    # TODO: admin
    inlines = [PlacementInlineOptions, SeriePartInlineAdmin, TaggingInlineOptions]
#    inlines = [PlacementInlineOptions, TaggingInlineOptions]

    rich_text_fields = {None: ('perex', 'description',)}


class SeriePartAdmin(EllaAdminOptionsMixin, admin.ModelAdmin):
    # TODO: admin
    list_display = ('target_admin', 'serie', 'part_no',)
#    list_filter = ('serie','target_ct',)

admin.site.register(Serie, SerieAdmin)
admin.site.register(SeriePart, SeriePartAdmin)