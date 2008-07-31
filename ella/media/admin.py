from django.contrib import admin

from ella.media.models import Media
from ella.core.admin import PlacementInlineOptions

from ella.tagging.admin import TaggingInlineOptions


class MediaOptions(admin.ModelAdmin):
    inlines = (FormattedMediaInlineOptions,)
    prepopulated_fields = {'slug' : ('title',)}

    list_display = ('title',)
    list_filter = ('uploaded',)
    search_fields = ('title', 'slug', 'description', 'content',)

    raw_id_fields = ('photo',)

    inlines = (PlacementInlineOptions, TaggingInlineOptions,)

    rich_text_fields = {None: ('description', 'content',)}


admin.site.register(Media, MediaOptions)
