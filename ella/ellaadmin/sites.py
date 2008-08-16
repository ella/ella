import copy

from django import http
from django.db import models
from django.contrib import admin
from django.views.decorators.cache import never_cache
from django.contrib.contenttypes.models import ContentType
from django.utils import simplejson

from ella.core.cache import get_cached_object_or_404
from ella.ellaadmin.options import EllaAdminOptionsMixin
from ella.ellaadmin.utils import admin_url


class EllaAdminSite(admin.AdminSite):
    def __init__(self, admin_opts=object):
        super(EllaAdminSite, self).__init__()
        self._registry = admin.site._registry
        self.admin_opts = admin_opts

    def mixin_admin(self, admin_class):
        """dynamically add custom admin_opts as other base class"""
        if self.admin_opts not in admin_class.__bases__:
            class Mix(admin_class, self.admin_opts): pass
            Mix.__bases__ = Mix.__bases__ + admin_class.__bases__
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
         #   admin_obj.__class__ = self.mixin_admin(admin_obj.__class__)
         #   for i in admin_obj.inline_instances:
         #       i.__class__ = self.mixin_admin(i.__class__)
        except KeyError:
            raise http.Http404("This model exists but has not been registered with the admin site.")
        return admin_obj(request, rest_of_url)
    model_page = never_cache(model_page)


    def root(self, request, url):
        try:
            return super(EllaAdminSite, self).root(request, url)
        except http.Http404:
            if url.startswith('ella/'):
                return self.root_ella(request, url)
            raise

    def root_ella(self, request, url):
        url = url.lstrip('ella/')
        url = url.rstrip('/')

        if url.startswith('cache/status'):
            from ella.ellaadmin.memcached import cache_status
            return cache_status(request)

        if url.split('/')[0].isdigit():
            url_parts = url.split('/')
            contenttype = get_cached_object_or_404(ContentType, pk=url_parts[0])
            url_parts.pop(0)
            return self.root_contenttype(request, contenttype, *url_parts)

        raise http.Http404

    def root_contenttype(self, request, contenttype, *url_parts):
        """
        prepare redirect to admin_list view, objects change_view,
        other special views (delete, history, ..) and hook our own views
        """
        get_params = request.GET and '?%s' % request.GET.urlencode() or ''
        changelist_view = '../../%s/%s' % (contenttype.app_label, contenttype.model,)

        if not len(url_parts):
            # redirect to admin changelist list for this contet type
            redir = '%s/%s' % (changelist_view, get_params)
            return http.HttpResponseRedirect(redir)

        if not url_parts[0].isdigit:
            # we don't handle actions on content type itself
            raise http.Http404

        if len(url_parts) == 1:
            # redirect to admin change view for specific object
            redir = '../%s/%s/%s' % (changelist_view, url_parts[0], get_params)
            return http.HttpResponseRedirect(redir)

        if len(url_parts) == 2 and url_parts[1] == 'info':
            # object_detail for some ajax raw_id widget
            mimetype = 'text/html' or 'application/json' # ?:)
            obj = get_cached_object_or_404(contenttype, pk=url_parts[0])
            response = {
                'name': str(obj),
                'content_type_name': contenttype.name,
                'content_type': contenttype.model,
                'url': getattr(obj, 'get_absolute_url', lambda:None)(),
                'admin_url': admin_url(obj),
}
            return http.HttpResponse(simplejson.dumps(response, indent=2), mimetype=mimetype)

        if len(url_parts) == 2:
            # some action on specific object (delete, history, ..)
            redir = '../../%s/%s/%s/%s' % (changelist_view, url_parts[0], url_parts[1], get_params)
            return http.HttpResponseRedirect(redir)

        raise http.Http404


site = EllaAdminSite(EllaAdminOptionsMixin)

