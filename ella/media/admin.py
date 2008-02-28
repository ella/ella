from django.contrib import admin

from ella.media.models import Type, Source, Format, FormattedFile


class FormattedFileInlineOptions(admin.TabularInline):
    model = FormattedFile
    extra = 2
    fieldsets = ((None, {'fields' : ('format', 'url', 'status',)}),)

class FormattedFileOptions(admin.ModelAdmin):
    list_display = ('__unicode__', 'hash', 'source', 'format',)
    raw_id_fields = ('source',)

class SourceOptions(admin.ModelAdmin):
    inlines = (FormattedFileInlineOptions,)
    prepopulated_fields = {'slug' : ('title',)}

    list_display = ('title', 'hash', 'type',)
    list_filter = ('type', 'uploaded',)
    search_fields = ('title', 'slug', 'description',)


admin.site.register([ Type, Format, ])
admin.site.register(Source, SourceOptions)
admin.site.register(FormattedFile, FormattedFileOptions)

