from django.contrib.auth.backends import ModelBackend
from django.conf import settings

class EllaModelBackend(ModelBackend):
    """
    Django AuthBackend based on ModelBackend. If passed a user object and asked
    for its permission, it will additionaly return all the permissions granted to the user on a per-site basis.
    """
    def get_all_permissions(self, user_obj):
        if not hasattr(user_obj, '_perm_cache'):
            # get built-in permissions
            user_obj._perm_cache = ModelBackend.get_all_permissions(self, user_obj)

            # get permissions based on site roles
            user_obj._perm_cache.update([
                    u"%s.%s" % (p.content_type.app_label, p.codename)
                        for sur in user_obj.siteuserrole_set.select_related().filter(site__id=settings.SITE_ID)
                        for p in sur.group.permissions.select_related()
                ])

            # ..and category
            user_obj._perm_cache.update([
                    u"%s.%s" % (p.content_type.app_label, p.codename)
                        for cur in user_obj.categoryuserrole_set.select_related().filter(category__site__id=settings.SITE_ID)
                        for p in sur.group.permissions.select_related()
                ])

        return user_obj._perm_cache

