from django.conf.urls.defaults import *
from django.http import HttpResponse
import datetime

from django.db import models
from django.utils.translation import ugettext as _

from ella.core.models import Category
from ella.newman.sites import site
from ella.newman.options import NewmanModelAdmin
from ella.newman import models as m
from ella.newman.filterspecs import filter_spec
from ella.newman.permission import is_category_fk, is_site_fk, applicable_categories
from ella.newman.utils import user_category_filter, get_user_config
from ella.newman.config import CATEGORY_FILTER

class DevMessageAdmin(NewmanModelAdmin):
    list_display = ('title', 'author', 'version', 'ts',)
    prepopulated_fields = {'slug': ('title',)}

    def save_model(self, request, obj, form, change):
        if not obj.id:
            obj.author = request.user
        obj.save()


class HelpItemAdmin(NewmanModelAdmin):
    list_display = ('__unicode__',)
    list_filter = ('ct', 'lang',)
    list_select_related = False


class CategoryUserRoleAdmin(NewmanModelAdmin):
    list_filter = ('user', 'group',)
    list_display = ('user', 'group',)

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

site.register(m.DevMessage, DevMessageAdmin)
site.register(m.AdminHelpItem, HelpItemAdmin)
site.register(m.CategoryUserRole, CategoryUserRoleAdmin)

# testing Options from register.py
import register


# Category filter -- restricted categories accordingly to CategoryUserRoles and categories filtered via AdminSettings.
# custom registered DateField filter. Filter is inserted to the beginning of filter chain.
@filter_spec(lambda field: is_category_fk(field))
def category_field_filter(fspec):
    qs = Category.objects.filter(pk__in=applicable_categories(fspec.user))
    for cat in user_category_filter(qs, fspec.user):
        lookup_var = '%s__%s__exact' % (fspec.field_path, fspec.f.rel.to._meta.pk.name)
        link = ( cat, {lookup_var: cat.pk})
        fspec.links.append(link)
    return True

@filter_spec(lambda field: is_site_fk(field))
def site_field_filter(fspec):
    category_ids = get_user_config(fspec.user, CATEGORY_FILTER)
    if not category_ids:
        category_ids = m.DenormalizedCategoryUserRole.objects.root_categories_by_user(fspec.user)
    qs = Category.objects.filter(pk__in=category_ids)
    print qs
    sites = map(lambda c: c.site, qs)
    for site in sites:
        #category__site__id__exact=1
        lookup_var = '%s__%s__exact' % (fspec.field_path, fspec.f.rel.to._meta.pk.name)
        link = ( site, {lookup_var: site.pk})
        fspec.links.append(link)
    return True

