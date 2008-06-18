from django.contrib import admin
from django.utils.translation import ugettext as _
from django import newforms as forms
from django.newforms import models as modelforms
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from ella.ellaadmin import widgets
from ella.core.middleware import get_current_request
from ella.core.models import Author, Source, Category, Listing, HitCount, Placement
from ella.core.cache import get_cached_list

class PlacementForm(modelforms.ModelForm):

    class Meta:
        model = Placement

    def __init__(self, *args, **kwargs):
        initial = []
        if 'initial' in kwargs:
            initial = [ c.id for c in Category.objects.distinct().filter(listing__placement=kwargs['initial']['id']) ]

        self.base_fields['listings'] = modelforms.ModelMultipleChoiceField(Category.objects.all(), cache_choices=True, required=False, initial=initial)
        super(PlacementForm, self).__init__(*args, **kwargs)


class PlacementInlineFormset(generic.GenericInlineFormset):

    def save_existing(self, form, instance, commit=True):
        instance = super(PlacementInlineFormset, self).save_existing(form, instance, commit)
        return self.save_listings(form, instance, commit)

    def save_new(self, form, commit=True):
        instance = super(PlacementInlineFormset, self).save_new(form, commit)
        return self.save_listings(form, instance, commit)

    def save_listings(self, form, instance, commit=True):
        list_cats = form.cleaned_data.pop('listings')

        def save_listings():
            listings = dict([ (l.category, l) for l in Listing.objects.filter(placement=instance.pk) ])

            for c in list_cats:
                if not c in listings:
                    # create listing
                    l = Listing(placement=instance, category=c, publish_from=instance.publish_from)
                    l.save()
                else:
                    del listings[c]
            for l in listings.values():
                l.delete()

        if commit:
            save_listings()
        else:
            save_m2m = form.save_m2m
            def save_all():
                save_m2m()
                save_listings()
            form.save_m2m = save_all
        return instance

    def clean (self):
        # no data - nothing to validate
        if not self.is_valid() or not self.cleaned_data or not self.instance or not self.cleaned_data[0]:
            return

        obj = self.instance
        cat = getattr(obj, 'category', None)
        obj_slug = getattr(obj, 'slug', obj.pk)
        target_ct=ContentType.objects.get_for_model(obj)

        main = None
        for d in self.cleaned_data:
            # empty form
            if not d: break

            if cat and cat == d['category']:
                main = d


            # allow placements that do not overlap
            q = Q(publish_to__isnull=True, publish_to__lt=d['publish_from'])
            if d['publish_to']:
                q |= Q(publish_from__gt=d['publish_to'])

            slug = d.get('slug', obj_slug)
            # try and find conflicting placement
            qset = Placement.objects.filter(q,
                category=d['category'],
                target_ct=target_ct,
                slug=slug,
                static=d['static'],
)

            # check for same date in URL
            if not d['static']:
                qset = qset.filter(
                    publish_from__year=d['publish_from'].year,
                    publish_from__month=d['publish_from'].month,
                    publish_from__day=d['publish_from'].day,
)

            # exclude current object from search
            if d['id']:
                qset = qset.exclude(pk=d['id'])

            if qset:
                plac = qset[0]
                raise forms.ValidationError(
                        _('There is already a Placement object published in category %(category)s with slug %(slug)s referring to %(target)s.') % {
                            'slug' : slug,
                            'category' : plac.category,
                            'target' : plac.target,
})

        if cat and not main:
            raise forms.ValidationError(_('If object has a category, it must have a main placement.'))

        return

class ListingInlineOptions(admin.TabularInline):
    model = Listing
    extra = 3

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'category':
            kwargs['widget'] = widgets.ListingCategoryWidget
        return super(self.__class__, self).formfield_for_dbfield(db_field, **kwargs)

class PlacementInlineOptions(generic.GenericTabularInline):
    model = Placement
    extra = 2
    ct_field_name = 'target_ct'
    id_field_name = 'target_id'
    formset = PlacementInlineFormset
    form = PlacementForm
    fieldsets = [ (None, {'fields' : ('category','publish_from', 'publish_to', 'slug', 'static', 'listings',)}), ]

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'category':
            kwargs['widget'] = widgets.ListingCategoryWidget
        return super(self.__class__, self).formfield_for_dbfield(db_field, **kwargs)

class PlacementOptions(admin.ModelAdmin):
    list_display = ('target', 'category', 'publish_from', 'full_url',)
    list_filter = ('publish_from', 'category', 'target_ct',)
    inlines = [ ListingInlineOptions, ]

class CategoryOptions(admin.ModelAdmin):
    list_filter = ('site',)
    list_display = ('draw_title', 'tree_path', '__unicode__')
    ordering = ('site', 'tree_path',)
    prepopulated_fields = {'slug': ('title',)}

class HitCountOptions(admin.ModelAdmin):
    list_display = ('target', 'hits',)
    list_filter = ('placement__target_ct', 'placement__category__site',)

class AuthorOptions(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(HitCount, HitCountOptions)
admin.site.register(Category, CategoryOptions)
admin.site.register(Source)
admin.site.register(Author, AuthorOptions)
admin.site.register(Placement, PlacementOptions)

