from django import template
from django.contrib import admin as django_admin
from django.shortcuts import render_to_response
from django.utils.functional import update_wrapper
from django.utils.translation import ugettext, ugettext_lazy as _
from django.core.exceptions import ImproperlyConfigured

from ella.newman.forms import SiteFilterForm
from django.views.decorators.http import require_POST
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.mail import EmailMessage
from ella.newman.decorators import require_AJAX
from ella.newman.models import AdminSetting

NEWMAN_URL_PREFIX = 'nm'

class NewmanSite(django_admin.AdminSite):

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        # Newman specific URLs
        urlpatterns = patterns('',
            url(r'^%s/err-report/$' % NEWMAN_URL_PREFIX,
                wrap(self.err_report),
                name="newman-err-report"),
            url(r'^%s/save-filters/$' % NEWMAN_URL_PREFIX,
                wrap(self.cat_filters_save),
                name="newman-save-filters"),
#            url(r'^$',
#                wrap(self.index),
#                name='%sadmin_index' % self.name),
        )
        urlpatterns += super(NewmanSite, self).get_urls()
        return urlpatterns

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

    @require_AJAX
    def err_report(self, request, extra_context=None):
        """
        Sends error report or feature request to administrator.
        """

        from django.conf import settings
        u, s, m = request.user, request.POST.get('subj'), request.POST.get('msg')

        if s and m:
            try:
                e = EmailMessage('Newman report: %s' % s, m,
                                 from_email=u.email, to=settings.ERR_REPORT_RECIPIENTS)
                e.send()
                return HttpResponse(content=ugettext('Your report was sent.'), mimetype='text/plain', status=200)
            except:
                return HttpResponse(content=ugettext('SMTP error.'), mimetype='text/plain', status=405)

        return HttpResponse(content=ugettext('Subject or message is empty.'), mimetype='text/plain', status=405)

    @require_AJAX
    def cat_filters_save(self, request, extra_content=None):

        site_filter_form = SiteFilterForm(user=request.user, data=request.POST)
        if site_filter_form.is_valid():
            o, c = AdminSetting.objects.get_or_create(
                user = request.user,
                var = 'cat_filters'
            )
            o.val = '%s' % site_filter_form.cleaned_data['sites']
            o.save()

            return HttpResponse(content=ugettext('Your settings was saved.'), mimetype='text/plain', status=200)
        else:
            return HttpResponse(content=ugettext('Error in form.'), mimetype='text/plain', status=405)


site = NewmanSite()
