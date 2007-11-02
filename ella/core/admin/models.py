from django.contrib import admin
from django.utils.translation import ugettext
from django import newforms as forms
from django.contrib.contenttypes import generic

from ella.ellaadmin import widgets

class ListingInlineFormset(generic.GenericInlineFormset):
    def clean (self):
        if not self.cleaned_data or not self.instance:
            return self.cleaned_data

        obj = self.instance
        cat = obj.category

        main = None
        for d in self.cleaned_data:
            if d['category'] == cat:
                main = d
                qset = obj.__class__._default_manager.filter(slug=obj.slug, category=obj.category_id)
                if obj._get_pk_val():
                    qset = qset.exclude(pk=obj._get_pk_val())

                for o in qset:
                    if o.main_listing and o.main_listing.publish_from.date() == d['publish_from'].date():
                        raise forms.ValidationError(ugettext('There is already an object published in category %(category)s with slug %(slug)s on %(date)s') % {
                                    'slug' : obj.slug,
                                    'category' : obj.category,
                                    'date' : d['publish_from'].date(),
})

            elif d['hidden']:
                raise forms.ValidationError, ugettext('Only main listing can be hidden.')
        if main is None:
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

class DependencyOptions(admin.ModelAdmin):
    list_filter = ('source_ct', 'target_ct',)
    list_display = ('source_ct', 'source', 'target_ct', 'target',)

class CategoryOptions(admin.ModelAdmin):
    list_filter = ('site',)
    list_display = ('draw_title', 'tree_path')
    ordering = ('tree_path',)
    prepopulated_fields = {'slug': ('title',)}

class HitCountOptions(admin.ModelAdmin):
    list_display = ('target', 'hits',)
    list_filter = ('target_ct', 'site',)

class AuthorOptions(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

