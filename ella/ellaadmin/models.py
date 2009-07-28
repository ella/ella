"""
First semi-working draft of category-based permissions. It will allow permissions to be set per-site and per category
effectively hiding the content the user has no permission to see/change.
"""
from django.db import models
from django.contrib import admin
from django.contrib.sites.models import Site
from django.contrib.auth.models import User, Group, Permission
from django.utils.translation import ugettext_lazy as _, ugettext

from ella.core.models import Category
from ella.core.cache import get_cached_object

#TODO @cache_this
def has_category_permission(user, model, category, permission):
    if user.has_perm(permission):
        return True

    app_label, code = permission.split('.', 1)
    perm = get_cached_object(Permission, content_type__app_label=app_label, codename=code)

    if CategoryUserRole.objects.filter(
            category=category,
            user=user,
            group__permissions=perm
        ).count():
        return True

    # fallback to site permissions
    return has_site_permission(user, model, category.site_id, permission)

def has_site_permission(user, model, site, permission):
    if user.has_perm(permission):
        return True

    app_label, code = permission.split('.', 1)
    perm = get_cached_object(Permission, content_type__app_label=app_label, codename=code)

    if SiteUserRole.objects.filter(site=site, user=user, group__permissions=perm).count():
        return True

    return False

def applicable_sites(user, permission=None):
    q = SiteUserRole.objects.filter(user=user).distinct().values('site')
    if permission:
        app_label, code = permission.split('.', 1)
        perm = get_cached_object(Permission, content_type__app_label=app_label, codename=code)
        q = q.filter(group__permissions=perm)
    else:
        # take any permission
        q = q.filter(group__permissions__id__isnull=False)
    return [ d['site'] for d in q ]



def applicable_categories(user, permission=None):
    q = CategoryUserRole.objects.filter(user=user).distinct().values('category')

    if permission:
        app_label, code = permission.split('.', 1)
        perm = Permission.objects.get(content_type__app_label=app_label, codename=code)
        q = q.filter(group__permissions=perm)
    else:
        # take any permission
        q = q.filter(group__permissions__id__isnull=False)

    return [ d['category'] for d in q ]

class CategoryUserRole(models.Model):
    """
    Apply all group's permission for the given user to this category.
    """
    user = models.ForeignKey(User, related_name="categoryuserrole_ellaadmin_set")
    group = models.ForeignKey(Group, related_name="categoryuserrole_ellaadmin_set")
    category = models.ForeignKey(Category, related_name="categoryuserrole_ellaadmin_set")

    def __unicode__(self):
        return ugettext(u'User %(user)s is a %(group)s for %(category)s.') % {
                'user' : self.user,
                'group' : self.group,
                'category' : self.category,
    }

    class Meta:
        verbose_name = _("User role in category")
        verbose_name_plural = _("User roles in categories")

class SiteUserRole(models.Model):
    """
    Apply all group's permission for the given user to this site.
    """
    user = models.ForeignKey(User)
    group = models.ForeignKey(Group)
    site = models.ForeignKey(Site)

    def __unicode__(self):
        return ugettext(u'User %(user)s is a %(group)s for %(site)s.') % {
                'user' : self.user,
                'group' : self.group,
                'site' : self.site,
    }

    class Meta:
        verbose_name = _("User role in site")
        verbose_name_plural = _("User roles in site")

class SiteUserRoleOptions(admin.ModelAdmin):
    list_filter = ('user', 'group', 'site',)
    list_display = ('user', 'group', 'site',)

class CategoryUserRoleOptions(admin.ModelAdmin):
    list_filter = ('user', 'group', 'category',)
    list_display = ('user', 'group', 'category',)

