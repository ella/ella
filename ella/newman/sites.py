from django import template
from django.contrib import admin as django_admin
from django.shortcuts import render_to_response
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ImproperlyConfigured
from ella.newman.forms import SiteFilterForm


class NewmanSite(django_admin.AdminSite):

# TODO: more dependencies in newman.
#    def check_dependencies(self):
#        """
#        Check that all things needed to run the admin have been correctly installed.
#
#        The default implementation checks that LogEntry, ContentType and the
#        auth context processor are installed.
#        """
#
#        super(NewmanSite, self).check_dependencies()
#        continue here...


# TODO: register newman's own URLs...
#    def get_urls(self):
#        from django.conf.urls.defaults import patterns, url, include
#
#        def wrap(view):
#            def wrapper(*args, **kwargs):
#                return self.admin_view(view)(*args, **kwargs)
#            return update_wrapper(wrapper, view)
#
#        urlpatterns = super(NewmanSite, self).get_urls()
#
#        urlpatterns += patterns('',
#
#)
#
#        # Admin-site-wide views.
#        urlpatterns = patterns('',
#            url(r'^$',
#                wrap(self.index),
#                name='%sadmin_index' % self.name),
#            url(r'^logout/$',
#                wrap(self.logout),
#                name='%sadmin_logout'),
#            url(r'^password_change/$',
#                wrap(self.password_change),
#                name='%sadmin_password_change' % self.name),
#            url(r'^password_change/done/$',
#                wrap(self.password_change_done),
#                name='%sadmin_password_change_done' % self.name),
#            url(r'^jsi18n/$',
#                wrap(self.i18n_javascript),
#                name='%sadmin_jsi18n' % self.name),
#            url(r'^r/(?P<content_type_id>\d+)/(?P<object_id>.+)/$',
#                'django.views.defaults.shortcut'),
#            url(r'^(?P<app_label>\w+)/$',
#                wrap(self.app_index),
#                name='%sadmin_app_list' % self.name),
#)
#
#        # Add in each model's views.
#        for model, model_admin in self._registry.iteritems():
#            urlpatterns += patterns('',
#                url(r'^%s/%s/' % (model._meta.app_label, model._meta.module_name),
#                    include(model_admin.urls))
#)
#        return urlpatterns

    def index(self, request, extra_context=None):
        """
        Displays the main Newman index page, without installed apps.
        """

        site_filter_form = SiteFilterForm(user=request.user)

        context = {
            'title': _('Site administration'),
            'site_filter_form': site_filter_form,
        }
        context.update(extra_context or {})
        return render_to_response(self.index_template or 'admin/index.html', context,
            context_instance=template.RequestContext(request)
)

site = NewmanSite()
