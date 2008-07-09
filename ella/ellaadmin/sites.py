import copy

from django.db import models
from django.contrib import admin
from django.views.decorators.cache import never_cache

from ella.ellaadmin.options import EllaAdminOptionsMixin


class EllaAdminSite(admin.AdminSite):
    def __init__(self, admin_opts=object):
        super(EllaAdminSite, self).__init__()
        self._registry = admin.site._registry
        self.admin_opts = admin_opts

    def mixin_admin(self, admin_class):
        """dynamically add custom admin_opts as other base class"""
        if self.admin_opts not in admin_class.__bases__:
            class Mix(self.admin_opts, admin_class): pass
            return Mix
        return admin_class

    def model_page(self, request, app_label, model_name, rest_of_url=None):
        """
        Handles the model-specific functionality of the admin site, delegating
        to the appropriate ModelAdmin class.

        patched version of django.contrib.admin.sites.AdminSite.model_page
        """
        model = models.get_model(app_label, model_name)
        if model is None:
            raise http.Http404("App %r, model %r, not found." % (app_label, model_name))
        try:
            admin_obj = copy.deepcopy(self._registry[model])
            admin_obj.admin_site = self
            admin_obj.__class__ = self.mixin_admin(admin_obj.__class__)
            for i in admin_obj.inline_instances:
                i.__class__ = self.mixin_admin(i.__class__)
        except KeyError:
            raise http.Http404("This model exists but has not been registered with the admin site.")
        return admin_obj(request, rest_of_url)
    model_page = never_cache(model_page)

    def root(self, request, url):
        try:
            return super(EllaAdminSite, self).root(request, url)
        except http.Http404:
            url = url.rstrip('/') # Trim trailing slash, if it exists.
            if url.startswith('e/cache/status'):
                from ella.ellaadmin.memcached import cache_status
                return cache_status(request)
            elif url == 'object_info':
                return self.object_info(request)
            else:
                raise


my_admin_site = EllaAdminSite(EllaAdminOptionsMixin)

