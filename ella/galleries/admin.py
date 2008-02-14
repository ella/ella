from django.contrib import admin
from ella.galleries.models import Gallery, GalleryItem
from ella.ellaadmin import fields, widgets
from ella.core.admin.models import ListingInlineOptions
from tagging.models import TaggingInlineOptions
from django.utils.translation import ugettext_lazy as _


class GalleryItemOptions(admin.ModelAdmin):
    """TODO: pridat widget, ktery bude volat maximuv skript"""
    pass

class GalleryItemTabularOptions(admin.TabularInline):
    model = GalleryItem
    extra = 10

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'order':
            kwargs['widget'] = widgets.IncrementWidget
        return super(self.__class__, self).formfield_for_dbfield(db_field, **kwargs)

class GalleryOptions(admin.ModelAdmin):
    list_display = ('title', 'created', 'category', 'full_url',)
    ordering = ('-created',)
    fieldsets = (
        (_("Gallery heading"), {'fields': ('title', 'slug',)}),
        (_("Gallery metadata"), {'fields': ('description', 'content', 'owner', 'category')}),
)
    list_filter = ('created', 'category',)
    search_fields = ('title', 'description', 'slug',)
    inlines = (GalleryItemTabularOptions, ListingInlineOptions, TaggingInlineOptions,)
    prepopulated_fields = {'slug': ('title',)}

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'description' or db_field.name == 'content':
            return fields.RichTextAreaField(**kwargs)
        return super(self.__class__, self).formfield_for_dbfield(db_field, **kwargs)

admin.site.register(Gallery, GalleryOptions)
