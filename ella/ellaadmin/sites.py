import copy

from django import http
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
            if url.startswith('ella/cache/status'):
                from ella.ellaadmin.memcached import cache_status
                return cache_status(request)
            elif url == 'object_info':
                # TODO: make the same as previous - startswith('ella/...')
                # even more - ella/content_type -> admin list for app/model
                #             ella/content_type/id -> app/model/id
                return self.object_info(request)
            else:
                raise

    def object_info(self, request):
        from django.utils import simplejson
        from django.http import HttpResponse, HttpResponseBadRequest, Http404
        from django.db.models import ObjectDoesNotExist
        from ella.core.cache import get_cached_object_or_404
        from django.contrib.contenttypes.models import ContentType
        response = {}
        #mimetype = 'application/json'
        mimetype = 'text/html'

        if not request.GET.has_key('ct_id') or not request.GET.has_key('ob_id'):
            return HttpResponseBadRequest()

        ct_id = request.GET['ct_id']
        ob_id = request.GET['ob_id']

        ct = get_cached_object_or_404(ContentType, pk=ct_id)
        response['content_type_name'] = ct.name
        response['content_type'] = ct.model

        ob = get_cached_object_or_404(ct, pk=ob_id)
        response['name'] = str(ob)
        if hasattr(ob, 'get_absolute_url'):
            response['url'] = ob.get_absolute_url()
        response['admin_url'] = reverse('admin', args=['%s/%s/%d' % (ct.app_label, ct.model, ob.pk)])

        return HttpResponse(simplejson.dumps(response, indent=2), mimetype=mimetype)


site = EllaAdminSite(EllaAdminOptionsMixin)

