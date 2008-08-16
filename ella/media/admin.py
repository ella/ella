from django.contrib import admin

from ella.media.models import Media, Format, FormattedMedia
from ella.core.admin import PlacementInlineOptions
from ella.tagging.admin import TaggingInlineOptions
from ella.ellaadmin.options import EllaAdminOptionsMixin

class FormattedMediaInlineOptions(admin.TabularInline):
    model = FormattedMedia
    extra = 2
    fieldsets = ((None, {'fields' : ('format', 'url', 'status',)}),)

class FormattedMediaOptions(EllaAdminOptionsMixin, admin.ModelAdmin):
    list_display = ('__unicode__', 'hash', 'source', 'format',)
    raw_id_fields = ('source',)

class MediaOptions(EllaAdminOptionsMixin, admin.ModelAdmin):
    inlines = (FormattedMediaInlineOptions,)
    prepopulated_fields = {'slug' : ('title',)}

    list_display = ('title', 'hash',)
    list_filter = ('uploaded',)
    search_fields = ('title', 'slug', 'description', 'content',)

    raw_id_fields = ('photo',)

    inlines = (PlacementInlineOptions, TaggingInlineOptions,)

    rich_text_fields = {None: ('description', 'content',)}


admin.site.register(Format)
admin.site.register(Media, MediaOptions)
admin.site.register(FormattedMedia, FormattedMediaOptions)

