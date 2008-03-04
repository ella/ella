from django.contrib import admin
from django.utils.translation import ugettext_lazy as _, ugettext
from django.newforms.models import InlineFormset
from django import newforms as forms
from django.contrib.contenttypes.models import ContentType

from tagging.models import TaggingInlineOptions

from ella.galleries.models import Gallery, GalleryItem
from ella.ellaadmin import fields, widgets
from ella.core.admin import ListingInlineOptions
from ella.core.cache import get_cached_object


class GalleryItemFormset(InlineFormset):
    " Override default FormSet to allow for custom validation."

    def clean (self):
        """Searches for duplicate references to the same object in one gallery."""
        if not self.cleaned_data or not self.instance:
            return self.cleaned_data

        obj = self.instance
        items = set([])

        for d in self.cleaned_data:
            # TODO: why cleaned data does not have target_ct_id prop?
            target = (d['target_ct'].id, d['target_id'],)
            # check for duplicities
            if target in items:
                obj = get_cached_object(get_cached_object(ContentType, pk=d['target_ct'].id), pk=d['target_id'])
                raise forms.ValidationError, ugettext('There are two references to %s in this gallery') % obj
            items.add(target)

        return self.cleaned_data

class GalleryItemTabularOptions(admin.TabularInline):
    model = GalleryItem
    extra = 10
    formset = GalleryItemFormset

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
            if db_field.blank:
                kwargs['required'] = False
            return fields.RichTextAreaField(**kwargs)
        return super(self.__class__, self).formfield_for_dbfield(db_field, **kwargs)

admin.site.register(Gallery, GalleryOptions)
