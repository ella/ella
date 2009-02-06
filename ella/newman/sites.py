import copy

from django import http
from django.db import models
from django.contrib import admin
from django.views.decorators.cache import never_cache
from django.contrib.contenttypes.models import ContentType

class NewmanSite(admin.AdminSite):
    def __init__(self, admin_opts=object):
        super(NewmanSite, self).__init__()
        self._registry = admin.site._registry
        self.admin_opts = admin_opts

    def register(self, model_or_iterable, admin_class=None, **options):
        super(NewmanSite, self).register(model_or_iterable, admin_class, **options)

    def model_page(self, request, app_label, model_name, rest_of_url=None):
        # TODO zaridit, aby se mohla zavolat jen super metoda (problem je kvuli tridni promenne admin_site)
        #return super(NewmanSite, self).model_page(request, app_label, model_name, rest_of_url)
        model = models.get_model(app_label, model_name)
        if model is None:
            raise http.Http404("App %r, model %r, not found." % (app_label, model_name))
        try:
            admin_obj = copy.deepcopy(self._registry[model])
            admin_obj.admin_site = self
        except KeyError:
            raise http.Http404("This model exists but has not been registered with the admin site.")
        return admin_obj(request, rest_of_url)

    def root(self, request, url):
        return super(NewmanSite, self).root(request, url)

site = NewmanSite()
