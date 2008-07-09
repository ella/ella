from django.contrib import admin

from ella.media.models import Media, Format, FormattedMedia
from ella.core.admin import PlacementInlineOptions
from ella.ellaadmin import fields

from ella.tagging.admin import TaggingInlineOptions


class FormattedMediaInlineOptions(admin.TabularInline):
    model = FormattedMedia
    extra = 2
    fieldsets = ((None, {'fields' : ('format', 'url', 'status',)}),)

class FormattedMediaOptions(admin.ModelAdmin):
    list_display = ('__unicode__', 'hash', 'source', 'format',)
    raw_id_fields = ('source',)

class MediaOptions(admin.ModelAdmin):
    inlines = (FormattedMediaInlineOptions,)
    prepopulated_fields = {'slug' : ('title',)}

    list_display = ('title', 'hash',)
    list_filter = ('uploaded',)
    search_fields = ('title', 'slug', 'description', 'content',)

    raw_id_fields = ('photo',)

    inlines = (PlacementInlineOptions, TaggingInlineOptions,)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in ['description', 'content']:
            kwargs['required'] = not db_field.blank
            return fields.RichTextAreaField(**kwargs)
        return super(MediaOptions, self).formfield_for_dbfield(db_field, **kwargs)

admin.site.register(Format)
admin.site.register(Media, MediaOptions)
admin.site.register(FormattedMedia, FormattedMediaOptions)

