from ella import newman
from django.utils.translation import ugettext_lazy as _

from ella.series.models import Serie, SeriePart
from ella.core.newman_admin import PlacementInlineAdmin, PublishableAdmin


class SeriePartInlineAdmin(newman.NewmanTabularInline):
    model = SeriePart
    extra = 5
    raw_id_fields = ('placement',)


class SerieAdmin(PublishableAdmin):
    list_filter = ('started', 'finished',)


    fieldsets = (
        (None, {'fields': ('title', 'slug', 'photo')}),
        (_("Metadata"), {'fields': ('category', 'authors', ('started', 'finished'), 'hide_newer_parts',),}),
        (_("Description"), {'fields': ('description', 'text', ), 'classes': ('small',)}),
    )

    raw_id_fields = ('photo',)
    rich_text_fields = {None: ('description', 'text',)}

    inlines = [PlacementInlineAdmin, SeriePartInlineAdmin]



class SeriePartAdmin(newman.NewmanModelAdmin):
    # TODO: admin
    list_display = ('target_admin', 'serie', 'published',)
    raw_id_fields = ('placement',)
    list_filter = ('serie',)

    def target_admin(self, obj):
        return obj.target
    target_admin.short_description = _('Target')


newman.site.register(Serie, SerieAdmin)
newman.site.register(SeriePart, SeriePartAdmin)


