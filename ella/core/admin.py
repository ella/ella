from django.contrib import admin
from django.forms import models as modelforms
from django.forms.fields import DateTimeField
from django.forms.util import ValidationError
from django.forms.models import save_instance, ModelMultipleChoiceField
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from ella.ellaadmin import widgets
from ella.core.models import Author, Source, Category, Listing, HitCount, Placement

class PlacementForm(modelforms.ModelForm):
    """PlacementForm from ella.core.newman_admin without djangomarkup dependency (and default Django fields)."""
    # create the field here to pass validation
    #listings =  fields.ListingCustomField(Category.objects.all(), label=_('Category'), cache_choices=True, required=False)
    listings = ModelMultipleChoiceField(Category.objects.all(), label=_('Category'), cache_choices=True, required=False)

    class Meta:
        model = Placement

    def __init__(self, *args, **kwargs):
        initial = []
        # args[data] -> instance
        if 'initial' in kwargs:
            initial = [ c.pk for c in Category.objects.distinct().filter(listing__placement=kwargs['initial']['id']) ]
        elif 'instance' in kwargs:
            initial = [ list(kwargs['instance'].listing_set.all()) ]

        #self.base_fields['listings'] = fields.ListingCustomField(
        #        Category.objects.all(), label=_('Category'), cache_choices=True, required=False, initial=initial)
        self.base_fields['listings'] = self.base_fields['listings'].__class__(
                 Category.objects.all(), label=_('Category'), cache_choices=True, required=False, initial=initial)
        super(PlacementForm, self).__init__(*args, **kwargs)

    def get_publish_date(self, pub_from):
        " Tries to save publish_from field specified either by POST parameter or by Placement (self.instance). "
        if pub_from:
            dt_field = DateTimeField()
            return dt_field.clean(pub_from)
        return self.instance.publish_from

    def save(self, commit=True):
        cleaned_list_cats = self.cleaned_data.pop('listings')
        list_cats = []
        # Order of items should be preserved (in cleaned_data is order not preserved)
        for pk in self.data.getlist( self.get_part_id('') ):
            list_cats.append(Category.objects.get(pk=int(pk)))
        publish_from_fields = self.data.getlist(self.get_part_id('publish_from'))
        instance = self.instance

        def save_them():
            if not list_cats:
                return
            listings = dict([ (l.category, l) for l in Listing.objects.filter(placement=instance.pk) ])
            forloop_counter = 0 # used for counting delete checkboxes
            for c, pub in zip(list_cats, publish_from_fields):
                forloop_counter += 1
                delete_listing = self.data.get(self.get_part_id('%d-DELETE' % forloop_counter), 'off')
                if delete_listing == 'on':
                    # skip following for-cycle body, so the listing will be deleted
                    continue
                publish_from = self.get_publish_date(pub)
                if not c in listings:
                    # create listing
                    l = Listing(
                        placement=instance,
                        category=c,
                        publish_from=publish_from
                    )
                    l.save()
                else:
                    del listings[c]
                    lst = Listing.objects.filter(placement=instance, category=c)
                    if not lst:
                        continue
                    l = lst[0]
                    # if publish_from differs, modify Listing object
                    if l.publish_from != publish_from:
                        l.publish_from = publish_from
                        l.save()
            for l in listings.values():
                l.delete()

        if commit:
            save_them()
        else:
            save_m2m = getattr(self, 'save_m2m', None)
            def save_all():
                if save_m2m:
                    save_m2m()
                save_them()
            self.save_m2m = save_all
        instance.category = self.cleaned_data['category']
        instance.publish_from = self.cleaned_data['publish_from']
        instance.publish_to = self.cleaned_data['publish_to']
        instance.slug = self.cleaned_data['slug']
        instance.static = self.cleaned_data['static']
        if not commit:
            return instance
        if self.instance.pk is None:
            fail_message = 'created'
        else:
            fail_message = 'changed'
        return save_instance(self, instance, self._meta.fields,
                             fail_message, commit, exclude=self._meta.exclude)

    def get_part_id(self, suffix):
        id_part = self.data.get('placement_listing_widget')
        if not suffix:
            return id_part
        return '%s-%s' % (id_part, suffix)

    def listings_clean(self, placement_publish_from, data):
        # get listing category, publish_from and publish_to
        pub_from = data.getlist(self.get_part_id('publish_from'))
        listings = self.cleaned_data['listings']
        if pub_from and len(pub_from) != len(listings):
            raise ValidationError(_('Duplicate listings'))
        for lst, pub in zip(listings, pub_from):
            if not pub:
                #raise ValidationError(_('This field is required'))
                continue
            dt_field = DateTimeField()
            publish_from = dt_field.clean(pub)
            if publish_from < placement_publish_from:
                raise ValidationError(_('No listing can start sooner than main listing'))

    def clean(self):
        # no data - nothing to validate
        if not self.is_valid() or not self.cleaned_data or not self.instance or not self.cleaned_data['publishable']:
            return self.cleaned_data

        obj = self.instance
        cat = None
        if obj.pk:
            cat = getattr(obj, 'category', None)
        obj_slug = getattr(obj, 'slug', obj.pk)
        # if Placement has no slug, slug from Publishable object should be considered in following checks:
        if not obj_slug:
            obj_slug = self.cleaned_data['publishable'].slug

        main = None
        d = self.cleaned_data
        # empty form
        if not d:
            return self.cleaned_data
        #if cat and cat == cat and cat: # should be equiv. if cat:...
        if cat:
            main = d

        if d['publish_to'] and d['publish_from'] > d['publish_to']:
            raise ValidationError(_('Publish to must be later than publish from.'))

        d['slug'] = obj_slug
        # try and find conflicting placement
        qset = Placement.objects.filter(
            category=d['category'],
            slug=d['slug'],
            #publishable=obj,
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
            qset = qset.exclude(pk=d['id'].pk)
        if qset:
            plac = qset[0]
            # raise forms.ValidationError(
            raise ValidationError(
                    _('''There is already a Placement object published in
                    category %(category)s with the same URL referring to %(target)s.
                    Please change the slug or publish date.''') % {
                        'category' : plac.category,
                        'target' : plac.publishable,
                    })

        if cat and not main:
            # raise forms.ValidationError(_('If object has a category, it must have a main placement.'))
            raise (_('If object has a category, it must have a main placement.'))

        self.listings_clean(d['publish_from'], self.data)
        return self.cleaned_data

class PlacementInlineAdmin(admin.TabularInline):
    exclude = ('slug',)
    # template = 'newman/edit_inline/placement.html'
    template = 'admin/edit_inline/placement.html'
    model = Placement
    max_num = 1
    suggest_fields = {'category': ('__unicode__', 'title', 'slug',)}

    form = PlacementForm
    #formset = PlacementInlineFormset

"""
class PlacementInlineAdmin(admin.TabularInline):
    model = Placement
    max_num = 1
    #formset = PlacementInlineFormset
    form = PlacementForm
    extra = 1
    '''
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
    '''
"""


class ListingForm(modelforms.ModelForm):
    class Meta:
        model = Listing

class ListingInlineAdmin(admin.TabularInline):
    model = Listing
    extra = 2
    fieldsets = ((None, {'fields' : ('category','publish_from', 'priority_from', 'priority_to', 'priority_value', 'commercial',)}),)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'category':
            kwargs['widget'] = widgets.ListingCategoryWidget
        return super(ListingInlineAdmin, self).formfield_for_dbfield(db_field, **kwargs)


class HitCountInlineAdmin(admin.TabularInline):
    model = HitCount
    extra = 0

class PlacementAdmin(admin.ModelAdmin):
    pass
    '''
    list_display = ('target_admin', 'category', 'publish_from', 'full_url',)
    list_filter = ('publish_from', 'category', 'target_ct',)
    inlines = (ListingInlineOptions,)
    fieldsets = (
        (_('target'), {'fields': ('target_ct', 'target_id', 'slug', 'category',), 'classes': ('wide',)},),
        (_('time'), {'fields': ('publish_from','publish_to', 'static',), 'classes': ('wide',)},),
    )
    '''

class ListingAdmin(admin.ModelAdmin):
    pass
    '''
    list_display = ('target_admin', 'target_ct', 'publish_from', 'category', 'placement_admin', 'target_hitcounts', 'target_url',)
    list_display_links = ()
    list_filter = ('publish_from', 'category__site', 'category', 'placement__target_ct',)
    raw_id_fields = ('placement',)
    date_hierarchy = 'publish_from'
    '''

class CategoryAdmin(admin.ModelAdmin):
    list_filter = ('site',)
    list_display = ('draw_title', 'tree_path', '__unicode__')
    search_fields = ('title', 'slug',)
    #ordering = ('site', 'tree_path',)
    prepopulated_fields = {'slug': ('title',)}

class HitCountAdmin(admin.ModelAdmin):
    list_display = ('target', 'hits',)
    ordering = ('-hits', '-last_seen',)

class AuthorAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

class SourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'url',)
    search_fields = ('name',)

class PublishableAdmin(admin.ModelAdmin):
    """ Default admin options for all publishables """

    list_display = ('title', 'category',)
    list_filter = ('category', 'authors',)
    search_fields = ('title', 'description', 'slug', 'authors__name', 'authors__slug',) # FIXME: 'tags__tag__name',)
    raw_id_fields = ('photo',)
    prepopulated_fields = {'slug' : ('title',)}
    rich_text_fields = {None: ('description',)}

    suggest_fields = {
        'category': ('tree_path', 'title', 'slug',),
        'authors': ('name', 'slug', 'email',),
        'source': ('name', 'url',),
    }

    #inlines = [PlacementInlineAdmin]


admin.site.register(HitCount, HitCountAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Source, SourceAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Placement, PlacementAdmin)
admin.site.register(Listing, ListingAdmin)
