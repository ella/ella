from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from ella.series.models import Serie, SeriePart
from ella.ellaadmin.options import EllaAdminOptionsMixin, EllaModelAdmin
from ella.core.admin import PlacementInlineAdmin


class SeriePartInlineAdmin(EllaAdminOptionsMixin, admin.TabularInline):
    model = SeriePart
    extra = 5
    raw_id_fields = ('placement',)


class SerieAdmin(EllaAdminOptionsMixin, EllaModelAdmin):
    list_display = ('title', 'photo_thumbnail', 'started', 'is_active', 'parts_count',)
    list_filter = ('started', 'finished',)
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'description',)

    fieldsets = (
        (None, {'fields': ('title',)}),
        (_("Slug, metadata"), {'fields': ('slug', 'started', 'finished', 'hide_newer_parts',), 'classes': ['collapse'],}),
        (_("Contents"), {'fields': ('description', 'category', 'photo',)}),
    )

    raw_id_fields = ('photo',)
    rich_text_fields = {None: ('description',)}

    inlines = [PlacementInlineAdmin, SeriePartInlineAdmin]



class SeriePartAdmin(EllaAdminOptionsMixin, admin.ModelAdmin):
    # TODO: admin
    list_display = ('target_admin', 'serie', 'published',)
    raw_id_fields = ('placement',)
    list_filter = ('serie',)

    def target_admin(self, obj):
        return obj.target
    target_admin.short_description = _('Target')

admin.site.register(Serie, SerieAdmin)
admin.site.register(SeriePart, SeriePartAdmin)
