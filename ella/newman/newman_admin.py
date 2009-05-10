import time

from django.conf.urls.defaults import *
from django.http import HttpResponse
from django.utils.translation import ugettext as _

from ella import newman
from ella.core.models.main import Category
from ella.core.models.publishable import Placement


from ella.newman import models as m
from ella.newman.filterspecs import filter_spec
from ella.newman.permission import is_category_fk, is_site_fk, applicable_categories
from ella.newman.utils import user_category_filter, get_user_config
from ella.newman.config import CATEGORY_FILTER

class DevMessageAdmin(newman.NewmanModelAdmin):
    list_display = ('title', 'author', 'version', 'ts',)
    prepopulated_fields = {'slug': ('title',)}

    def save_model(self, request, obj, form, change):
        if not obj.id:
            obj.author = request.user
        obj.save()


class HelpItemAdmin(newman.NewmanModelAdmin):
    list_display = ('__unicode__',)
    list_filter = ('ct', 'lang',)
    rich_text_fields = {'': ('long',)}
    list_select_related = False

class CategoryUserRoleAdmin(newman.NewmanModelAdmin):
    list_filter = ('user', 'group',)
    list_display = ('user', 'group',)
    suggest_fields = {'category': ('title', 'tree_path',)}

    def get_urls(self):
        urls = patterns('',
            url(r'^refresh/$',
                self.refresh_view,
                name='categoryuserrole-refresh'),
        )
        urls += super(CategoryUserRoleAdmin, self).get_urls()
        return urls

    def refresh_view(self, request, extra_context=None):
        from ella.newman.management.commands.syncroles import denormalize
        # TODO: don't wait for denormalize()
        denormalize()
        return HttpResponse(_('All roles is now refreshed.'))

newman.site.register(m.DevMessage, DevMessageAdmin)
newman.site.register(m.AdminHelpItem, HelpItemAdmin)
newman.site.register(m.CategoryUserRole, CategoryUserRoleAdmin)

# Category filter -- restricted categories accordingly to CategoryUserRoles and categories filtered via AdminSettings.
# custom registered DateField filter. Filter is inserted to the beginning of filter chain.
category_lookup = lambda fspec: '%s__%s__exact' % (fspec.field_path, fspec.f.rel.to._meta.pk.name)

@filter_spec(lambda field: is_category_fk(field), category_lookup)
def category_field_filter(fspec):
    qs = Category.objects.filter(pk__in=applicable_categories(fspec.user))
    for cat in user_category_filter(qs, fspec.user):
        lookup_var = '%s__%s__exact' % (fspec.field_path, fspec.f.rel.to._meta.pk.name)
        link = ( cat, {lookup_var: cat.pk})
        fspec.links.append(link)
    return True

site_lookup = lambda fspec: '%s__%s__exact' % (fspec.field_path, fspec.f.rel.to._meta.pk.name)
@filter_spec(lambda field: is_site_fk(field), site_lookup)
def site_field_filter(fspec):
    category_ids = get_user_config(fspec.user, CATEGORY_FILTER)
    if not category_ids:
        if not fspec.user.is_superuser:
            category_ids = m.DenormalizedCategoryUserRole.objects.root_categories_by_user(fspec.user)
        else:
            category_ids = Category.objects.filter(tree_parent=None)
    qs = Category.objects.filter(pk__in=category_ids)
    sites = map(lambda c: c.site, qs)
    for site in sites:
        #category__site__id__exact=1
        lookup_var = '%s__%s__exact' % (fspec.field_path, fspec.f.rel.to._meta.pk.name)
        link = ( site, {lookup_var: site.pk})
        fspec.links.append(link)
    return True

#@filter_spec(lambda field: field.name.lower() == 'created' and isinstance(field, models.DateTimeField))
PUBLISHED_FROM_FIELD_PATH = 'placement__listing__publish_from'
def published_from_lookup(fspec):
    out = [
        '%s__day' % PUBLISHED_FROM_FIELD_PATH,
        '%s__month' % PUBLISHED_FROM_FIELD_PATH,
        '%s__year' % PUBLISHED_FROM_FIELD_PATH,
    ]
    return out
@filter_spec(lambda field: field.name.lower() == 'created', published_from_lookup, title=_('Publish from'))
def publish_from_filter(fspec):
    # SELECT created FROM qs._meta.dbtable  GROUP BY created
    #qs = fspec.model_admin.queryset(fspec.request)
    #dates =  qs.dates(fspec.field_path, 'day', 'DESC')[:365]
    # Article.objects.filter(placement__listing__publish_from__gte='2012-01-01')
    ts = time.time() - (365*24*60*60)
    last_year = time.strftime('%Y-%m-%d %H:%M', time.localtime(ts))
    qs = Placement.objects.filter(listing__publish_from__gte=last_year)
    dates = qs.dates('publish_from', 'day', 'DESC')
    for date in dates:
        lookup_dict = dict()
        lookup_dict['%s__day' % PUBLISHED_FROM_FIELD_PATH] = date.day
        lookup_dict['%s__month' % PUBLISHED_FROM_FIELD_PATH] = date.month
        lookup_dict['%s__year' % PUBLISHED_FROM_FIELD_PATH] = date.year
        link_text = '%d. %d. %d' % (date.day, date.month, date.year)
        link = ( link_text, lookup_dict)
        fspec.links.append(link)
    return True

