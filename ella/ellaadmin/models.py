import management
'''
from django.db import models
from django.contrib.auth.models import User, Group
from django.contrib.sites.models import Site

from ella.core.models import Category

#@cache_this
def has_permission(user, category, permission):
    for ec in EnableCategory.objects.filter(category=categry, user=user):
        if ec.group.permission_set.fliter(pk=permission.pk).count():
            return True

    for es in EnableSite.objects.filter(site=category.site_id, user=user):
        if es.group.permission_set.fliter(pk=permission.pk).count():
            return True

    return False

#SELECT DISTINCT category FROM EnableCategory JOIN permission_group USING group_id WHERE user_id = 2 AND permission_id = 1;

class EnableCategory(models.Model):
    """
    Apply all group's permission for the given user to this category.
    """
    user = models.ForeignKey(User)
    group = models.ForeignKey(Group)
    category = models.ForeignKey(Category)

class EnableSite(models.Model):
    """
    Apply all group's permission for the given user to this site.
    """
    user = models.ForeignKey(User)
    group = models.ForeignKey(Group)
    site = models.ForeignKey(Site)
'''

