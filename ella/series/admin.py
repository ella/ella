from django.contrib import admin
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext_lazy as _

from ella.series.models import Serie, SeriePart
from ella.ellaadmin.options import EllaAdminOptionsMixin
from ella.core.admin import PlacementInlineOptions
from ella.tagging.admin import TaggingInlineOptions


class SeriePartInlineAdmin(EllaAdminOptionsMixin, admin.TabularInline):
    model = SeriePart
    extra = 5
    raw_id_fields = ('placement',)


class SerieAdmin(EllaAdminOptionsMixin, admin.ModelAdmin):
    list_display = ('title', 'photo_thumbnail', 'started', 'is_active', 'parts_count', 'get_hits',)
    list_filter = ('started', 'finished',)
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'perex',)

    fieldsets = (
        (None, {'fields': ('title',)}),
        (_("Slug, metadata"), {'fields': ('slug', 'started', 'finished', 'hide_newer_parts',), 'classes': ['collapse'],}),
        (_("Contents"), {'fields': ('perex', 'description', 'category', 'photo',)}),
)

    raw_id_fields = ('photo',)
    rich_text_fields = {None: ('perex', 'description',)}

    inlines = [PlacementInlineOptions, SeriePartInlineAdmin, TaggingInlineOptions]


class SeriePartAdmin(EllaAdminOptionsMixin, admin.ModelAdmin):
    # TODO: admin
    list_display = ('target_admin', 'serie', 'published',)
    raw_id_fields = ('placement',)
    list_filter = ('serie',)

admin.site.register(Serie, SerieAdmin)
admin.site.register(SeriePart, SeriePartAdmin)