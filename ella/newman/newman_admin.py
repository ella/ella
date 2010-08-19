from django.conf.urls.defaults import *
from django.http import HttpResponse
from django.utils.translation import ugettext as _

from ella import newman
from ella.core.models.main import Category

from ella.newman import models as m
from ella.newman.filterspecs import CustomFilterSpec
from ella.newman.permission import is_category_fk, applicable_categories
from ella.newman.utils import user_category_filter

class DevMessageAdmin(newman.NewmanModelAdmin):
    list_display = ('title', 'author', 'version', 'ts',)
    search_fields = ('title', 'summary', 'details',)
    list_filter = ('author', 'ts',)
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
    search_fields = ('user__username', 'category__title', 'category__slug')
    suggest_fields = {'category': ('__unicode__', 'title', 'slug',)}

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

class CategoryUserRoleInline(newman.NewmanTabularInline):
    model = m.CategoryUserRole
    max_num = 3
    suggest_fields = {'category': ('__unicode__', 'title', 'tree_path', 'slug', ) }

newman.site.register(m.DevMessage, DevMessageAdmin)
newman.site.register(m.AdminHelpItem, HelpItemAdmin)
newman.site.register(m.CategoryUserRole, CategoryUserRoleAdmin)

# Category filter -- restricted categories accordingly to CategoryUserRoles and categories filtered via AdminSettings.
# custom registered DateField filter. Filter is inserted to the beginning of filter chain.
class NewmanCategoryFilter(CustomFilterSpec):
    " customized Category filter. "

    def title(self):
        return _('Category')

    def get_lookup_kwarg(self):
        lookup_var = '%s__%s__exact' % (self.field.name, self.field.rel.to._meta.pk.name)
        return lookup_var

    def filter_func(self):
        qs = Category.objects.filter(pk__in=applicable_categories(self.user))
        lookup_var = self.get_lookup_kwarg()
        for cat in user_category_filter(qs, self.user):
            link = ( cat, {lookup_var: cat.pk})
            self.links.append(link)
        return True

    def generate_choice(self, **lookup_kwargs):
        category_id = lookup_kwargs.get(self.get_lookup_kwarg(), '')
        if not category_id or not category_id.isdigit():
            return None
        try:
            thing = Category.objects.get( pk=int(category_id) )
        except (Category.MultipleObjectsReturned, Category.DoesNotExist):
            return None
        return thing.__unicode__()
NewmanCategoryFilter.register_insert(lambda field: is_category_fk(field), NewmanCategoryFilter)

"""
site_lookup = lambda fspec: '%s__%s__exact' % (fspec.f.name, fspec.f.rel.get_related_field().name)
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
        lookup_var = '%s__%s__exact' % (fspec.f.name, fspec.f.rel.get_related_field().name)
        link = ( site, {lookup_var: site.pk})
        fspec.links.append(link)
    return True
"""
"""
class NewmanSiteFilter(CustomFilterSpec):
    " customized Site filter. "
    def title(self):
        return _('Site')

    def get_lookup_kwarg(self):
        lookup_var = '%s__%s__exact' % (self.field.name, self.field.rel.get_related_field().name)
        return lookup_var

    def filter_func(self):
        print('FILTER SITE')
        category_ids = get_user_config(self.user, CATEGORY_FILTER)
        if not category_ids:
            if not self.user.is_superuser:
                category_ids = m.DenormalizedCategoryUserRole.objects.root_categories_by_user(self.user)
            else:
                category_ids = Category.objects.filter(tree_parent=None)
        qs = Category.objects.filter(pk__in=category_ids)
        sites = map(lambda c: c.site, qs)
        lookup_var = self.get_lookup_kwarg()
        for site in sites:
            #category__site__id__exact=1
            link = ( site, {lookup_var: site.pk})
            self.links.append(link)
        return True

    def generate_choice(self, **lookup_kwargs):
        category_id = lookup_kwargs.get(self.get_lookup_kwarg(), '')
        if not category_id or not category_id.isdigit():
            return None
        try:
            thing = Site.objects.get( pk=int(category_id) )
        except (Site.MultipleObjectsReturned, Site.DoesNotExist):
            return None
        return thing.__unicode__()
NewmanCategoryFilter.register_insert(lambda field: is_site_fk(field), NewmanSiteFilter)
"""

# TODO: register some non-ella apps, fix it

class SiteAdmin(newman.NewmanModelAdmin):
    list_display = ('domain', 'name',)

from django.contrib.sites.models import Site
newman.site.register(Site, SiteAdmin)

from django.contrib.auth.admin import UserAdmin, GroupAdmin
class UserAdmin(UserAdmin, newman.NewmanModelAdmin):
    inlines = [CategoryUserRoleInline]
    suggest_fields = {'groups': ('name',)}

class GroupAdmin(GroupAdmin, newman.NewmanModelAdmin):
    pass

from django.contrib.auth.models import User, Group
newman.site.register(User, UserAdmin)
newman.site.register(Group, GroupAdmin)
