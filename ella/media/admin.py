from django.contrib import admin

from ella.media.models import Type, Media, Format, FormattedFile
from ella.core.admin import ListingInlineOptions
from ella.ellaadmin import fields

from tagging.models import TaggingInlineOptions


class FormattedFileInlineOptions(admin.TabularInline):
    model = FormattedFile
    extra = 2
    fieldsets = ((None, {'fields' : ('format', 'url', 'status',)}),)

class FormattedFileOptions(admin.ModelAdmin):
    list_display = ('__unicode__', 'hash', 'source', 'format',)
    raw_id_fields = ('source',)

class MediaOptions(admin.ModelAdmin):
    inlines = (FormattedFileInlineOptions,)
    prepopulated_fields = {'slug' : ('title',)}

    list_display = ('title', 'hash', 'type',)
    list_filter = ('type', 'uploaded',)
    search_fields = ('title', 'slug', 'description', 'content',)

    raw_id_fields = ('photo',)

    inlines = (ListingInlineOptions, TaggingInlineOptions,)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in ['description', 'content']:
            kwargs['required'] = not db_field.blank
            return fields.RichTextAreaField(**kwargs)
        return super(self.__class__, self).formfield_for_dbfield(db_field, **kwargs)

admin.site.register([ Type, Format, ])
admin.site.register(Media, MediaOptions)
admin.site.register(FormattedFile, FormattedFileOptions)

