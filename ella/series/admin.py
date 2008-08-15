from django.contrib import admin
from ella.series.models import Serie, SeriePart
from ella.ellaadmin.options import EllaAdminOptionsMixin

class SerieAdmin(EllaAdminOptionsMixin, admin.ModelAdmin):
    list_display = ('title', 'started', 'is_active')
    list_filter = ('started', 'finished',)
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'perex',)

    rich_text_fields = {None: ('description',)}


class SeriePartAdmin(EllaAdminOptionsMixin, admin.ModelAdmin):
    list_display = ('target', 'target_ct', 'serie', 'part_no',)
    list_filter = ('serie','target_ct',)

admin.site.register(Serie, SerieAdmin)
admin.site.register(SeriePart, SeriePartAdmin)

