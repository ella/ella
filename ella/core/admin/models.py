from django.contrib import admin
from django.utils.translation import ugettext
from django import newforms as forms
from django.contrib.contenttypes import generic

from ella.core.admin import widgets

class ListingInlineFormset(generic.GenericInlineFormset):
    def clean (self):
        if not self.cleaned_data or not self.instance:
            return self.cleaned_data

        obj = self.instance
        cat = obj.category

        for d in self.cleaned_data:
            if d['category'] == cat:
                main = d
            elif d['hidden']:
                raise forms.ValidationError, ugettext('Only main listing can be hidden.')
        else:
            raise forms.ValidationError, ugettext('If an object has a listing, it must have a listing in its main category.')

        if main['publish_from'] != min([ d['publish_from'] for d in self.cleaned_data]):
            raise forms.ValidationError, ugettext('No listing can start sooner than main listing')

        return self.cleaned_data

class ListingInlineOptions(generic.GenericTabularInline):
    @property
    def model(self):
        from ella.core.models import Listing
        return Listing
    extra = 2
    ct_field_name = 'target_ct'
    id_field_name = 'target_id'
    formset = ListingInlineFormset
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'category':
            kwargs['widget'] = widgets.ListingCategoryWidget
        return super(self.__class__, self).formfield_for_dbfield(db_field, **kwargs)


class ListingOptions(admin.ModelAdmin):
    list_display = ('target', 'category', 'publish_from', 'full_url',)
    list_filter = ('publish_from', 'category', 'target_ct',)
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'target_ct':
            kwargs['widget'] = widgets.ContentTypeWidget
        if db_field.name == 'target_id':
            kwargs['widget'] = widgets.ForeignKeyRawIdWidget
        return super(self.__class__, self).formfield_for_dbfield(db_field, **kwargs)

class DependencyOptions(admin.ModelAdmin):
    list_filter = ('source_ct', 'target_ct',)
    list_display = ('source_ct', 'source', 'target_ct', 'target',)
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'target_ct':
            kwargs['widget'] = widgets.ContentTypeWidget
        if db_field.name == 'target_id':
            kwargs['widget'] = widgets.ForeignKeyRawIdWidget
        if db_field.name == 'source_ct':
            kwargs['widget'] = widgets.ContentTypeWidget
        if db_field.name == 'source_id':
            kwargs['widget'] = widgets.ForeignKeyRawIdWidget
        return super(self.__class__, self).formfield_for_dbfield(db_field, **kwargs)

class CategoryOptions(admin.ModelAdmin):
    list_display = ('draw_title', 'tree_path')
    ordering = ('tree_path',)
    prepopulated_fields = {'slug': ('title',)}

class HitCountOptions(admin.ModelAdmin):
    list_display = ('target', 'hits', 'last_seen',)
    list_filter = ('last_seen', 'target_ct', 'site',)

class AuthorOptions(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

