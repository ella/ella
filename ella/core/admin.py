from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.forms import models as modelforms
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.conf import settings

from ella.ellaadmin import widgets
from ella.ellaadmin.options import EllaAdminOptionsMixin, EllaModelAdmin
from ella.core.models import Author, Source, Category, Listing, HitCount, Placement

class PlacementForm(modelforms.ModelForm):
    # create the field here to pass validation
    listings =  modelforms.ModelMultipleChoiceField(Category.objects.all(), label=_('Category'), cache_choices=True, required=False)

    class Meta:
        model = Placement

    def __init__(self, *args, **kwargs):
        initial = []
        if 'initial' in kwargs:
            initial = [ c.pk for c in Category.objects.distinct().filter(listing__placement=kwargs['initial']['id']) ]

        self.base_fields['listings'] = modelforms.ModelMultipleChoiceField(
                Category.objects.all(), label=_('Category'), cache_choices=True, required=False, initial=initial)
        super(PlacementForm, self).__init__(*args, **kwargs)


class PlacementInlineFormset(generic.BaseGenericInlineFormSet):

    def __init__(self, data=None, files=None, instance=None, save_as_new=None):
        self.can_delete = True
        super(PlacementInlineFormset, self).__init__(instance=instance, data=data, files=files)

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

            if cat and cat == cat and cat:
                main = d

            if d['slug'] and d['slug'] != '':
                slug = d['slug']
            else:
                slug = obj_slug

            # try and find conflicting placement
            qset = Placement.objects.filter(
                category=d['category'],
                slug=slug,
                target_ct=target_ct.pk,
                static=d['static']
)

            if d['static']: # allow placements that do not overlap
                q = Q(publish_to__lt=d['publish_from'])
                if d['publish_to']:
                    q |= Q(publish_from__gt=d['publish_to'])
                qset = qset.exclude(q)

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
                        _('''There is already a Placement object published in
                        category %(category)s with the same URL referring to %(target)s.
                        Please change the slug or publish date.''') % {
                            'category' : plac.category,
                            'target' : plac.target,
})

            '''
            qset = Placement.objects.filter(
                        target_id=obj.pk,
                        target_ct=target_ct,
)

            if 'id' in d:
                qset = qset.exclude(id=d['id'])

            if qset:
                raise forms.ValidationError('Chyba')
            '''

        if cat and not main:
            raise forms.ValidationError(_('If object has a category, it must have a main placement.'))

        return

class ListingInlineOptions(admin.TabularInline):
    model = Listing
    extra = 2
    fieldsets = ((None, {'fields' : ('category','publish_from', 'priority_from', 'priority_to', 'priority_value', 'remove', 'commercial',)}),)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'category':
            kwargs['widget'] = widgets.ListingCategoryWidget
        return super(ListingInlineOptions, self).formfield_for_dbfield(db_field, **kwargs)

class PlacementInlineOptions(generic.GenericTabularInline):
    model = Placement
    extra = 1
    ct_field = 'target_ct'
    ct_fk_field = 'target_id'
    formset = PlacementInlineFormset
    form = PlacementForm
    fieldsets = ((None, {'fields' : ('category', 'publish_from', 'publish_to', 'slug', 'static', 'listings',)}),)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'category':
            kwargs['widget'] = widgets.ListingCategoryWidget
        return super(PlacementInlineOptions, self).formfield_for_dbfield(db_field, **kwargs)


class HitCountInlineOptions(admin.TabularInline):
    model = HitCount
    extra = 0

class PlacementOptions(EllaAdminOptionsMixin, EllaModelAdmin):
    list_display = ('target_admin', 'category', 'publish_from', 'full_url',)
    list_filter = ('publish_from', 'category', 'target_ct',)
    inlines = (ListingInlineOptions,)
    fieldsets = (
        (_('target'), {'fields': ('target_ct', 'target_id', 'slug', 'category',), 'classes': ('wide',)},),
        (_('time'), {'fields': ('publish_from','publish_to', 'static',), 'classes': ('wide',)},),
)

class ListingOptions(EllaAdminOptionsMixin, EllaModelAdmin):
    list_display = ('target_admin', 'target_ct', 'publish_from', 'category', 'placement_admin', 'target_hitcounts', 'target_url',)
    list_display_links = ()
    list_filter = ('publish_from', 'category__site', 'category', 'placement__target_ct',)
    raw_id_fields = ('placement',)
    date_hierarchy = 'publish_from'

class CategoryOptions(EllaAdminOptionsMixin, EllaModelAdmin):
    list_filter = ('site',)
    list_display = ('draw_title', 'tree_path', '__unicode__')
    search_fields = ('title', 'slug',)
    ordering = ('site', 'tree_path',)
    prepopulated_fields = {'slug': ('title',)}

class HitCountOptions(admin.ModelAdmin):
    list_display = ('target', 'hits',)
    ordering = ('-hits', '-last_seen',)

class AuthorOptions(EllaAdminOptionsMixin, EllaModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

class SourceOptions(EllaAdminOptionsMixin, EllaModelAdmin):
    list_display = ('name', 'url',)

admin.site.register(HitCount, HitCountOptions)
admin.site.register(Category, CategoryOptions)
admin.site.register(Source, SourceOptions)
admin.site.register(Author, AuthorOptions)
admin.site.register(Placement, PlacementOptions)
admin.site.register(Listing, ListingOptions)

