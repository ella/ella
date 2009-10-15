from django.core.urlresolvers import reverse
import datetime, time

from django.utils.translation import ugettext_lazy as _, ugettext
from django.forms import models as modelforms
from django.forms.fields import DateTimeField
from django.db.models import Q
from django.forms.util import ValidationError
from django.forms.models import save_instance
from django.conf.urls.defaults import patterns, url
from django.utils.safestring import mark_safe
from django.template.defaultfilters import date
from django.conf import settings

from ella.core.models import Author, Source, Category, Listing, HitCount, Placement, Related, Publishable
from ella.core.models.publishable import PUBLISH_FROM_WHEN_EMPTY
from ella import newman
from ella.comments.models import Comment
from ella.newman import options, fields
from ella.newman.filterspecs import CustomFilterSpec, NewmanSiteFilter

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

    def listings_clean(self, data):
        # get listing category, publish_from and publish_to
        pub_from = data.getlist(self.get_part_id('publish_from'))
        listings = self.cleaned_data['listings']
        if len(pub_from) and (len(pub_from) != len(listings)):
            raise ValidationError(_('Amount of publish_from input fields should be the same as category fields. With kind regards Your PlacementInline and his ListingCustomWidget.'))
        for lst, pub in zip(listings, pub_from):
            if not pub:
                #raise ValidationError(_('This field is required'))
                continue
            dt_field = DateTimeField()
            publish_from = dt_field.clean(pub)

    def clean(self):
        # no data - nothing to validate
        if not self.is_valid() or not self.cleaned_data or not self.instance or not self.cleaned_data['publishable']:
            return self.cleaned_data

        obj = self.instance
        cat = None
        if obj.pk:
            cat = getattr(obj, 'category', None)
        obj_slug = getattr(obj, 'slug', obj.pk)

        main = None
        d = self.cleaned_data
        # empty form
        if not d:
            return self.cleaned_data
        #if cat and cat == cat and cat: # should be equiv. if cat:...
        if cat:
            main = d

        d['slug'] = obj_slug
        # try and find conflicting placement
        qset = Placement.objects.filter(
            category=d['category'],
            slug=d['slug'],
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
    suggest_fields = {'category': ('__unicode__', 'title', 'slug',)}
    fieldsets = ((None, {'fields' : ('category','publish_from', 'publish_to', 'priority_from', 'priority_to', 'priority_value', 'commercial',)}),)

class PlacementInlineAdmin(newman.NewmanTabularInline):
    exclude = ('slug',)
    template = 'newman/edit_inline/placement.html'
    model = Placement
    max_num = 1
    suggest_fields = {'category': ('__unicode__', 'title', 'slug',)}

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
    suggest_fields = {'tree_parent': ('__unicode__', 'title', 'slug')}

class HitCountAdmin(newman.NewmanModelAdmin):
    list_display = ('target', 'hits', 'target_url')
#    list_filter = ('placement__category', 'placement__publish_from')
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

class RelatedInlineAdmin(newman.GenericTabularInline):
    extra = 3
    model = Related
    ct_field = 'related_ct'
    ct_fk_field = 'related_id'
    suggest_fields = {'publishable': ('__unicode__', 'title', 'slug')}

class IsPublishedFilter(CustomFilterSpec):
    " Published/Nonpublished objects filter"
    lookup_var = 'publish_from'

    def title(self):
        return _('Is published?')

    def get_lookup_kwarg(self):
        for param in self.request_get:
            if param.startswith("%s__gt" % self.lookup_var) or param.startswith("%s__lte" % self.lookup_var):
                self.selected_lookup = param
                return param
        return ''

    def filter_func(self):
        # nepublikovany = nemaji placement (datum 3000) ci maji placement v budoucnu
        # ?publish_from__exact=2008-10-10
        lookup_var_not_published = '%s__gt' % self.lookup_var
        lookup_var_published = '%s__lte' % self.lookup_var
        now = time.strftime('%Y-%m-%d')
        link = ( _('No'), {lookup_var_not_published: now})
        self.links.append(link)
        link = ( _('Yes'), {lookup_var_published: now})
        self.links.append(link)
        self.remove_from_querystring = [lookup_var_published, lookup_var_not_published]
        return True

class PublishFromFilter(CustomFilterSpec):
    " Publish from customized filter. "
    published_from_field_path = 'publish_from'

    def title(self):
        return _('Publish from')

    def get_lookup_kwarg(self):
        out = [
            '%s__day' % self.published_from_field_path,
            '%s__month' % self.published_from_field_path,
            '%s__year' % self.published_from_field_path,
        ]
        return out

    def filter_func(self):
        # SELECT created FROM qs._meta.dbtable  GROUP BY created
        #qs = fspec.model_admin.queryset(fspec.request)
        #dates =  qs.dates(fspec.field_path, 'day', 'DESC')[:365]
        # Article.objects.filter(placement__listing__publish_from__gte='2012-01-01')
        YEAR = 365*24*60*60
        ts = time.time() - YEAR
        last_year = time.strftime('%Y-%m-%d %H:%M', time.localtime(ts))
        qs = Placement.objects.filter(listing__publish_from__gte=last_year)
        dates = qs.dates('publish_from', 'day', 'DESC')
        for date in dates:
            lookup_dict = dict()
            lookup_dict['%s__day' % self.published_from_field_path] = date.day
            lookup_dict['%s__month' % self.published_from_field_path] = date.month
            lookup_dict['%s__year' % self.published_from_field_path] = date.year
            link_text = '%d. %d. %d' % (date.day, date.month, date.year)
            link = ( link_text, lookup_dict)
            self.links.append(link)
        return True

class PlacementAdmin(newman.NewmanModelAdmin):
    list_display = ('publishable', 'category', 'publish_from',)
    list_filter = ('category',)
    unbound_list_filter = (NewmanSiteFilter, PublishFromFilter,)
    search_fields = ('publishable__title', 'category__title',)
    suggest_fields = {'category': ('__unicode__', 'title', 'slug',), 'publishable': ('title',)}

    inlines = [ListingInlineAdmin]


class PublishableAdmin(newman.NewmanModelAdmin):
    """ Default admin options for all publishables """

    exclude = ('content_type',)
    list_display = ('admin_link', 'category', 'photo_thumbnail', 'publish_from_nice', 'placement_link', 'site_icon', 'fe_link',)
    if Comment._meta.installed:
        list_display += ('comment_links',)
    list_filter = ('category', 'content_type')
    unbound_list_filter = (NewmanSiteFilter, PublishFromFilter, IsPublishedFilter,)
    search_fields = ('title', 'description', 'slug', 'authors__name', 'authors__slug',) # FIXME: 'tags__tag__name',)
    raw_id_fields = ('photo',)
    prepopulated_fields = {'slug' : ('title',)}
    rich_text_fields = {'small': ('description',)}
    ordering = ('-publish_from',)

    suggest_fields = {
        'category': ('__unicode__', 'title', 'slug', 'tree_path'),
        'authors': ('name', 'slug', 'email',),
        'source': ('name', 'url',),
    }

    inlines = [PlacementInlineAdmin, RelatedInlineAdmin]

    def admin_link(self, object):
        ct = object.content_type
        return mark_safe('<a class="js-hashadr cl-publishable-link %s" href="/%s/%s/%s/">%s</a>' % (ct.model, ct.app_label, ct.model, object.pk, object))
    admin_link.allow_tags = True
    admin_link.short_description = _('Publishable object')

    def site_icon(self, object):
        return mark_safe('%s' % object.category.site.name)
    site_icon.short_description = _('site')
    site_icon.allow_tags = True

    def fe_link(self, obj):
        if obj.publish_from.year < 3000:
            kwargs = {'content_type_id': obj.content_type.id, 'object_id': obj.pk}
            return mark_safe(
                '<a href="%s" class="icn web js-nohashadr">www</a>' %
                reverse('newman:obj-redirect', kwargs=kwargs)
            )
        else:
            return '---'
    fe_link.short_description = _('WWW')
    fe_link.allow_tags = True

    def comment_links(self, obj):
        if Comment._meta.installed:
            block = '<a href="%s">%s</a>' % (reverse('newman:block_comment', args=(obj.content_type_id, obj.id)), ugettext('block'))
            delete = '<a href="%s">%s</a>' % (reverse('newman:delete_related_comments', args=(obj.content_type_id, obj.id)), ugettext('delete'))
            return mark_safe('<ul><li>%s</li><li>%s</li></ul>' % (block, delete))
        else:
            return 'comments not installed'
    comment_links.short_description = _('Comment options')
    comment_links.allow_tags = True

    def publish_from_nice(self, obj):
        span_str = '<span class="%s">%s</span>'
        date_str = date(obj.publish_from, settings.DATETIME_FORMAT)

        if obj.publish_from.year >= 3000:
            return mark_safe(span_str % ('unpublished', ugettext('No placement')))
        elif obj.publish_from > datetime.datetime.now():
            return span_str % ('unpublished', date_str)
        return span_str % ('published', date_str)
    publish_from_nice.short_description = _('Publish from')
    publish_from_nice.admin_order_field = 'publish_from'
    publish_from_nice.allow_tags = True

    def photo_thumbnail(self, object):
        photo = object.get_photo()
        if photo:
            return mark_safe(photo.thumb())
        else:
            return mark_safe('<span class="form-error-msg">%s</span>' % ugettext('No main photo!'))
    photo_thumbnail.allow_tags = True
    photo_thumbnail.short_description = _('Photo')

    def placement_link(self, object):
        if object.main_placement:
            return mark_safe('<span class="published"><a class="hashadr" href="/core/placement/%d/">%s</a></span>' % (object.main_placement.pk, object.main_placement.category))
        return mark_safe('<span class="unpublished"><a class="hashadr" href="/core/placement/?publishable__exact=%d">%s</a></span>' % (object.id, ugettext('No main placement')))
    placement_link.allow_tags = True
    placement_link.short_description = _('Main placement')

    # TODO: check speed with select_related()
#    def queryset(self, request):
#        qs = super(PublishableAdmin, self).queryset(request)
#        return qs.select_related()

newman.site.register(HitCount, HitCountAdmin)
newman.site.register(Category, CategoryAdmin)
newman.site.register(Source, SourceAdmin)
newman.site.register(Author, AuthorAdmin)
newman.site.register(Placement, PlacementAdmin)
#newman.site.register(Listing, ListingAdmin)
newman.site.register(Publishable, PublishableAdmin)


