from django.core.urlresolvers import reverse
import time

from django.utils.translation import ugettext_lazy as _, ugettext
from django.forms import models as modelforms
from django.forms.util import ValidationError
from django.utils.safestring import mark_safe
from django.template.defaultfilters import date
from django.conf import settings

from ella.core.models import Author, Source, Category, Listing, Related, Publishable
from ella.utils.timezone import now

import ella_newman as newman
from ella_newman import options
from ella_newman.filterspecs import CustomFilterSpec, NewmanSiteFilter

class ListingForm(modelforms.ModelForm):
    def clean(self):
        d = super(ListingForm, self).clean()
        if not self.is_valid():
            return d
        if d['publish_to'] and d['publish_from'] > d['publish_to']:
            raise ValidationError(_('Publish to must be later than publish from.'))
        return d

    class Meta:
        model = Listing


class ListingInlineAdmin(newman.NewmanTabularInline):
    model = Listing
    extra = 2
    suggest_fields = {'category': ('__unicode__', 'title', 'slug',)}
    form = ListingForm
    fieldsets = ((None, {'fields' : ('category','publish_from', 'publish_to', 'commercial',)}),)
    template = 'newman/edit_inline/listing.html'



class ListingAdmin(newman.NewmanModelAdmin):
    form = ListingForm

class CategoryAdmin(newman.NewmanModelAdmin):
    list_display = ('__unicode__', 'title', 'tree_path')
    list_filter = ('site',)
    search_fields = ('title', 'slug',)
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('site', 'tree_path',)
    suggest_fields = {'tree_parent': ('__unicode__', 'title', 'slug')}

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
    lookup_var = 'publish_from'
    CAPTION_YES = _('Yes')
    CAPTION_NO = _('No')

    def title(self):
        return _('Is published?')

    def get_lookup_kwarg(self):
        for param in self.request_get:
            if param.startswith('%s__gt' % self.lookup_var) or param.startswith('%s__lt' % self.lookup_var):
                self.selected_lookup = param
                return param
        return ''

    def filter_func(self):
        # nepublikovany = nemaji placement (datum 3000) ci maji placement v budoucnu
        # ?publish_from__exact=2008-10-10
        lookup_var_not_published = '%s__gt' % self.lookup_var
        lookup_var_published = '%s__lte' % self.lookup_var
        lookup_var_has_placement = '%s__lt' % self.lookup_var
        now = time.strftime('%Y-%m-%d')
        link = ( self.CAPTION_NO, {lookup_var_not_published: now})
        self.links.append(link)
        link = ( self.CAPTION_YES, {lookup_var_published: now})
        self.links.append(link)
        self.remove_from_querystring = [lookup_var_published, lookup_var_not_published, lookup_var_has_placement]
        return True

    def generate_choice(self, **lookup_kwargs):
        param = self.get_lookup_kwarg()
        if not param:
            return None
        elif param.startswith('%s__gt' % self.lookup_var):
            return self.CAPTION_NO
        elif param.startswith('%s__lte' % self.lookup_var):
            return self.CAPTION_YES
        return None

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
        qs = Listing.objects.filter(publish_from__gte=last_year)
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

    def generate_choice(self, **lookup_kwargs):
        args = self.get_lookup_kwarg()
        day = lookup_kwargs[args[0]]
        month = lookup_kwargs[args[1]]
        year = lookup_kwargs[args[2]]
        return u'%s. %s. %s' % (day, month, year)

class PublishableAdmin(newman.NewmanModelAdmin):
    """ Default admin options for all publishables """

    list_display = ('admin_link', 'category', 'photo_thumbnail', 'publish_from_nice', 'site_icon', 'fe_link',)
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

    inlines = [ListingInlineAdmin]

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

    def publish_from_nice(self, obj):
        span_str = '<span class="%s">%s</span>'
        date_str = date(obj.publish_from, settings.DATETIME_FORMAT)

        if obj.publish_from.year >= 3000:
            return mark_safe(span_str % ('unpublished', ugettext('No placement')))
        elif not obj.is_published():
            return span_str % ('unpublished', date_str)
        return span_str % ('published', date_str)
    publish_from_nice.short_description = _('Publish from')
    publish_from_nice.admin_order_field = 'publish_from'
    publish_from_nice.allow_tags = True

    def photo_thumbnail(self, object):
        if object.photo:
            return mark_safe(options.thumb_html(object.photo))
        else:
            return mark_safe('<span class="form-error-msg">%s</span>' % ugettext('No main photo!'))
    photo_thumbnail.allow_tags = True
    photo_thumbnail.short_description = _('Photo')

newman.site.register(Category, CategoryAdmin)
newman.site.register(Source, SourceAdmin)
newman.site.register(Author, AuthorAdmin)
#newman.site.register(Listing, ListingAdmin)
newman.site.register(Publishable, PublishableAdmin)


