from django.contrib import admin
from ella.series.models import Serie, SeriePart
from ella.ellaadmin.options import EllaAdminOptionsMixin

from ella.core.admin import PlacementInlineOptions
from ella.tagging.admin import TaggingInlineOptions

class SeriePartInlineAdmin(EllaAdminOptionsMixin, admin.TabularInline):
    model = SeriePart
    extra = 5
    raw_id_fields = ('placement',)


class SerieAdmin(EllaAdminOptionsMixin, admin.ModelAdmin):
    list_display = ('title', 'started', 'is_active')
    list_filter = ('started', 'finished',)
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'perex',)

    raw_id_fields = ('photo',)
    rich_text_fields = {None: ('perex', 'description',)}

    # TODO: admin
    inlines = [PlacementInlineOptions, SeriePartInlineAdmin, TaggingInlineOptions]
#    inlines = [PlacementInlineOptions, TaggingInlineOptions]


class SeriePartAdmin(EllaAdminOptionsMixin, admin.ModelAdmin):
    # TODO: admin
    list_display = ('target_admin', 'serie', 'part_no',)
    raw_id_fields = ('placement',)
#    list_filter = ('serie','target_ct',)

admin.site.register(Serie, SerieAdmin)
admin.site.register(SeriePart, SeriePartAdmin)