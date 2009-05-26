import time

from django.utils.translation import ugettext_lazy as _, ugettext
from django.forms import models as modelforms
from django.forms.fields import DateTimeField
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.forms.util import ValidationError
from django.conf.urls.defaults import patterns, url
from django.utils.safestring import mark_safe

from ella.core.models import Author, Source, Category, Listing, HitCount, Placement, Related, Publishable
from ella.core.models.publishable import PUBLISH_FROM_WHEN_EMPTY
from ella import newman
from ella.newman import options, fields
from ella.newman.filterspecs import CustomFilterSpec

class ListingForm(modelforms.ModelForm):
    class Meta:
        model = Listing

class PlacementForm(modelforms.ModelForm):
    # create the field here to pass validation
    listings =  fields.ListingCustomField(Category.objects.all(), label=_('Category'), cache_choices=True, required=False)

    class Meta:
        model = Placement

    def __init__(self, *args, **kwargs):
        initial = []
        # args[data] -> instance
        print '__init__ args:', str(args) , kwargs
        if 'initial' in kwargs:
            initial = [ c.pk for c in Category.objects.distinct().filter(listing__placement=kwargs['initial']['id']) ]
        elif 'instance' in kwargs:
            initial = {
                'selected_categories': [ 
                    c.pk for c in Category.objects.distinct().filter(listing__placement=kwargs['instance'].pk) 
                ], 
                'listings': list(kwargs['instance'].listing_set.all())
            }

        self.base_fields['listings'] = fields.ListingCustomField(
                Category.objects.all(), label=_('Category'), cache_choices=True, required=False, initial=initial)
        super(PlacementForm, self).__init__(*args, **kwargs)

    def get_publish_date(self, elem_id):
        " Tries to save publish_from field specified either by POST parameter or by Placement (self.instance). "
        pub_from = self.data.get(self.get_part_id('%d-publish_from' % elem_id))
        if pub_from:
            dt_field = DateTimeField()
            return dt_field.clean(pub_from)
        return self.instance.publish_from

    def save(self, commit=True):
        list_cats = self.cleaned_data.pop('listings')
        instance = self.instance
        if not list_cats:
            return instance
        
        def save_them():
            listings = dict([ (l.category, l) for l in Listing.objects.filter(placement=instance.pk) ])

            for c in list_cats:
                publish_from = self.get_publish_date(c.pk)
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
        return instance

    def get_part_id(self, suffix):
        id_part = self.data.get('placement_listing_widget')
        return '%s-%s' % (id_part, suffix)

    def listings_clean(self, data):
        # get listing category, publish_from and publish_to
        for d in self.cleaned_data['listings']:
            pub_from = data.get(self.get_part_id('%d-publish_from' % d.pk), None)
            dt_field = DateTimeField()
            if not pub_from:
                #raise ValidationError(_('This field is required'))
                continue
            dt_field = DateTimeField()
            publish_from = dt_field.clean(pub_from)

    def clean(self):
        # no data - nothing to validate
        if not self.is_valid() or not self.cleaned_data or not self.instance or not self.cleaned_data['publishable']:
            return self.cleaned_data

        obj = self.instance
        cat = None
        if obj.pk:
            cat = getattr(obj, 'category', None)
        obj_slug = getattr(obj, 'slug', obj.pk)
        target_ct=ContentType.objects.get_for_model(obj)

        main = None
        d = self.cleaned_data
        # empty form
        if not d: 
            return self.cleaned_data
        #if cat and cat == cat and cat: # should be equiv. if cat:...  
        if cat:
            main = d

        if d['slug'] and d['slug'] != '':
            slug = d['slug']
        else:
            slug = obj_slug
        # try and find conflicting placement
        qset = Placement.objects.filter(
            category=d['category'],
            slug=slug,
            publishable=obj,
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
                        'target' : plac.target,
                    })

        if cat and not main:
            # raise forms.ValidationError(_('If object has a category, it must have a main placement.'))
            raise (_('If object has a category, it must have a main placement.'))
        
        self.listings_clean(self.data)
        return self.cleaned_data


class PlacementInlineFormset(options.NewmanInlineFormSet):

    def __init__(self, data=None, files=None, instance=None, save_as_new=None, prefix=None):
        self.can_delete = True
        super(PlacementInlineFormset, self).__init__(instance=instance, data=data, files=files, prefix=prefix)


class ListingInlineAdmin(newman.NewmanTabularInline):
    model = Listing
    extra = 2
    suggest_fields = {'category': ('title', 'slug',)}
    fieldsets = ((None, {'fields' : ('category','publish_from', 'publish_to', 'priority_from', 'priority_to', 'priority_value', 'commercial',)}),)

class PlacementInlineAdmin(newman.NewmanTabularInline):
    template = 'newman/edit_inline/placement.html'
    model = Placement
    max_num = 1
    suggest_fields = {'category': ('title', 'slug',)}

    form = PlacementForm
    formset = PlacementInlineFormset
    '''
    ct_field = 'target_ct'
    ct_fk_field = 'target_id'
    fieldsets = ((None, {'fields' : ('category', 'publish_from', 'publish_to', 'slug', 'static', 'listings',)}),)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'category':
            kwargs['widget'] = widgets.ListingCategoryWidget
        return super(PlacementInlineOptions, self).formfield_for_dbfield(db_field, **kwargs)
    '''


class HitCountInlineAdmin(newman.NewmanTabularInline):
    model = HitCount
    extra = 0

class PlacementAdmin(newman.NewmanModelAdmin):
    list_display = ('publishable', 'category', 'publish_from',)
    list_filter = ('publish_from', 'category__site',)
    search_fields = ('publishable__title', 'category__title',)
    suggest_fields = {'category': ('title', 'slug',), 'publishable': ('title',)}

    inlines = [ListingInlineAdmin]


class ListingAdmin(newman.NewmanModelAdmin):
    pass
    '''
    list_display = ('target_admin', 'target_ct', 'publish_from', 'category', 'placement_admin', 'target_hitcounts', 'target_url',)
    list_display_links = ()
    list_filter = ('publish_from', 'category__site', 'category', 'placement__target_ct',)
    raw_id_fields = ('placement',)
    date_hierarchy = 'publish_from'
    '''

class CategoryAdmin(newman.NewmanModelAdmin):
    list_display = ('__unicode__', 'title', 'tree_path')
    list_filter = ('site',)
    search_fields = ('title', 'slug',)
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('tree_path',)
    suggest_fields = {'tree_parent': ('title', 'slug')}

class HitCountAdmin(newman.NewmanModelAdmin):
    list_display = ('target', 'hits', 'target_url')
    list_filter = ('placement__category', 'placement__publish_from')
    search_fields = ('placement__category__title',)
    ordering = ('-hits', '-last_seen',)

    def target_url(self, object):
        target = object.target()
        return mark_safe('<a class="icn web" href="%s">%s</a>' % (target.get_absolute_url(), target))
    target_url.short_description = _('View on site')
    target_url.allow_tags = True

    def get_urls(self):

        info = self.admin_site.name, self.model._meta.app_label, self.model._meta.module_name

        urlpatterns = patterns('',
            url(r'^by-category/$',
                self.by_category_view,
                name='%sadmin_%s_%s_by_category' % info),
        )
        urlpatterns += super(HitCountAdmin, self).get_urls()
        return urlpatterns

    def by_category_view(self, request, extra_context={}):
        pass

class AuthorAdmin(newman.NewmanModelAdmin):
    list_display = ('name', 'user', 'email',)
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'email',)

class SourceAdmin(newman.NewmanModelAdmin):
    list_display = ('name', 'url',)
    search_fields = ('name',)

class RelatedInlineAdmin(newman.NewmanTabularInline):
    extra = 3
    model = Related

class IsPublishedFilter(CustomFilterSpec):
    " Published/Nonpublished objects filter"
    #lookup_var = 'placement__publish_from'
    lookup_var = 'publish_from'

    def title(self):
        return _('Cucurucucu Paloma')

    def get_lookup_kwarg(self):
        for param in self.request_get:
            if param.startswith(self.lookup_var):
                return param
        return ''

    def filter_func(fspec):
        # nepublikovany = nemaji placement (datum 3000) ci maji placement v budoucnu
        # ?placement__publish_from__exact=2008-10-10
        lookup_var_not_published = '%s__exact' % fspec.lookup_var
        lookup_var_published = '%s__lt' % fspec.lookup_var
        when = time.strftime('%Y-%m-%d', PUBLISH_FROM_WHEN_EMPTY.timetuple())
        link = ( _('Not published'), {lookup_var_not_published: when})
        fspec.links.append(link)
        link = ( _('Published'), {lookup_var_published: when})
        fspec.links.append(link)
        fspec.remove_from_querystring = [lookup_var_published, lookup_var_not_published]
        return True

class PublishableAdmin(newman.NewmanModelAdmin):
    """ Default admin options for all publishables """

    exclude = ('content_type',)
    list_display = ('admin_link', 'category', 'photo_thumbnail', 'publish_from', 'placement_link', 'site_icon')
    list_filter = ('category__site', 'category', 'authors', 'content_type', 'publish_from')
    unbound_list_filter = (IsPublishedFilter,)
    search_fields = ('title', 'description', 'slug', 'authors__name', 'authors__slug',) # FIXME: 'tags__tag__name',)
    raw_id_fields = ('photo',)
    prepopulated_fields = {'slug' : ('title',)}
    rich_text_fields = {None: ('description',)}
    ordering = ('-publish_from',)

    suggest_fields = {
        'category': ('title', 'slug', 'tree_path'),
        'authors': ('name', 'slug', 'email',),
        'source': ('name', 'url',),
    }

    inlines = [PlacementInlineAdmin, RelatedInlineAdmin]

    def admin_link(self, object):
        ct = object.content_type
        return mark_safe('<a class="hashadr" href="/%s/%s/%s/">%s: %s</a>' % (ct.app_label, ct.model, object.pk, _(ct.name), object))
    admin_link.allow_tags = True
    admin_link.short_description = _('Publishable object')

    def site_icon(self, object):
        return mark_safe('%s' % object.category.site.name)
    site_icon.short_description = _('site')
    site_icon.allow_tags = True

    def photo_thumbnail(self, object):
        photo = object.get_photo()
        if photo:
            return mark_safe(photo.thumb())
        else:
            return mark_safe('<div class="errors"><ul class="errorlist"><li>%s</li></ul></div>' % ugettext('No main photo!'))
    photo_thumbnail.allow_tags = True
    photo_thumbnail.short_description = _('Photo')

    def placement_link(self, object):
        if object.main_placement:
            return mark_safe('<a class="hashadr" href="/core/placement/%d/">%s</a>' % (object.main_placement.pk, object.main_placement.category))
    placement_link.allow_tags = True
    placement_link.short_description = _('Placement')


newman.site.register(HitCount, HitCountAdmin)
newman.site.register(Category, CategoryAdmin)
newman.site.register(Source, SourceAdmin)
newman.site.register(Author, AuthorAdmin)
newman.site.register(Placement, PlacementAdmin)
#newman.site.register(Listing, ListingAdmin)
newman.site.register(Publishable, PublishableAdmin)


