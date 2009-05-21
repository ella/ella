from django.utils.translation import ugettext_lazy as _, ugettext
from django.forms import models as modelforms
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.forms.util import ValidationError
from django.conf.urls.defaults import patterns, url
from django.utils.safestring import mark_safe

from ella.core.models import Author, Source, Category, Listing, HitCount, Placement, Related
from ella.core.models.publishable import Publishable
from ella import newman

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


class PlacementInlineFormset(newman.NewmanTabularInline):

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
                # raise forms.ValidationError(
                raise ValidationError(
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
                # raise forms.ValidationError('Chyba')
                raise ValidationError('Chyba')
            '''

        if cat and not main:
            # raise forms.ValidationError(_('If object has a category, it must have a main placement.'))
            raise (_('If object has a category, it must have a main placement.'))

        return

class ListingInlineAdmin(newman.NewmanTabularInline):
    model = Listing
    extra = 2
    suggest_fields = {'category': ('title', 'slug',)}
    fieldsets = ((None, {'fields' : ('category','publish_from', 'publish_to', 'priority_from', 'priority_to', 'priority_value', 'commercial',)}),)

class PlacementInlineAdmin(newman.NewmanTabularInline):
    model = Placement
    max_num = 1
    suggest_fields = {'category': ('title', 'slug',)}
    '''
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

class PublishableAdmin(newman.NewmanModelAdmin):
    """ Default admin options for all publishables """

    exclude = ('content_type',)
    list_display = ('admin_link', 'category', 'photo_thumbnail', 'publish_from', 'placement_link', 'site_icon')
    list_filter = ('category__site', 'category', 'authors', 'content_type')
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


