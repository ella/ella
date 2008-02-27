from django.contrib import admin
from django.utils.translation import ugettext as _
from django import newforms as forms
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from ella.ellaadmin import widgets
from ella.core.middleware import get_current_request
from ella.core.models import Author, Source, Category, Listing, HitCount, Dependency


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
                        raise forms.ValidationError(
                                _('There is already an object published in category %(category)s with slug %(slug)s on %(date)s') % {
                                    'slug' : obj.slug,
                                    'category' : obj.category,
                                    'date' : d['publish_from'].date(),
})

            elif d['hidden']:
                raise forms.ValidationError, _('Only main listing can be hidden.')

        # the main listing not present
        if main is None:
            try:
                # try to retrieve it from db
                main = Listing.objects.get(category=cat, target_ct=ContentType.objects.get_for_model(obj), target_id=obj._get_pk_val())
                main = main.__dict__
            except Listing.DoesNotExist:
                raise forms.ValidationError, _('If an object has a listing, it must have a listing in its main category.')

        if main['publish_from'] != min([ main['publish_from'] ] + [ d['publish_from'] for d in self.cleaned_data]):
            # TODO: move the error to the form that is at fault
            raise forms.ValidationError, _('No listing can start sooner than main listing')

        return self.cleaned_data

    '''
    def get_queryset(self):
        """
        Override the default so that Listings I don't have permissions to change won't show up
        """
        from ella.ellaadmin import applicable_categories

        if self.instance is None:
            return []

        return super(ListingInlineFormset, self).get_queryset().filter(category__in=applicable_categories(get_current_request().user, 'core.change_listing'))
    '''

class ListingInlineOptions(generic.GenericTabularInline):
    model = Listing
    extra = 2
    ct_field_name = 'target_ct'
    id_field_name = 'target_id'
    formset = ListingInlineFormset

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'category':
            kwargs['widget'] = widgets.ListingCategoryWidget
        return super(self.__class__, self).formfield_for_dbfield(db_field, **kwargs)

class HitCountInlineOptions(generic.GenericTabularInline):
    model = HitCount
    extra = 0
    ct_field_name = 'target_ct'
    id_field_name = 'target_id'
    list_display = ('last_seen', 'hits',)
    fieldsets = [ (None, {'fields': ('hits',)}) ]

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'hits':
            kwargs['widget'] = widgets.ParagraphInputWidget
        return super(self.__class__, self).formfield_for_dbfield(db_field, **kwargs)

class ListingOptions(admin.ModelAdmin):
    list_display = ('target', 'category', 'publish_from', 'full_url',)
    list_filter = ('publish_from', 'category', 'target_ct',)

class DependencyOptions(admin.ModelAdmin):
    list_filter = ('source_ct', 'target_ct',)
    list_display = ('source_ct', 'source', 'target_ct', 'target',)

class CategoryOptions(admin.ModelAdmin):
    list_filter = ('site',)
    list_display = ('draw_title', 'tree_path', '__unicode__')
    ordering = ('site', 'tree_path',)
    prepopulated_fields = {'slug': ('title',)}

class HitCountOptions(admin.ModelAdmin):
    list_display = ('target', 'hits',)
    list_filter = ('target_ct', 'site',)

class AuthorOptions(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(HitCount, HitCountOptions)
admin.site.register(Category, CategoryOptions)
admin.site.register(Source)
admin.site.register(Author, AuthorOptions)
admin.site.register(Listing, ListingOptions)
admin.site.register(Dependency , DependencyOptions)

