import datetime

from django import template
from django.contrib.admin.sites import AdminSite
from django.shortcuts import render_to_response
from django.utils.functional import update_wrapper
from django.utils.translation import ugettext, ugettext_lazy as _
from django.db import models
from django.http import HttpResponseRedirect, Http404
from django.core.mail import EmailMessage
from django.views.decorators.cache import never_cache
from django.contrib.auth import authenticate, login, logout
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from ella.core.cache.utils import get_cached_list
from ella.core.models.publishable import Placement, Publishable
from ella.newman.forms import SiteFilterForm, ErrorReportForm, EditorBoxForm
from ella.newman.models import AdminSetting
from ella.newman.decorators import require_AJAX
from ella.newman.utils import set_user_config_db, set_user_config_session, get_user_config,\
    JsonResponse, JsonResponseError, json_decode, user_category_filter
from ella.newman.permission import has_model_list_permission, applicable_categories, permission_filtered_model_qs
from ella.newman.config import CATEGORY_FILTER, NEWMAN_URL_PREFIX, STATUS_SMTP_ERROR, STATUS_FORM_ERROR,\
    NON_PUBLISHABLE_CTS
from ella.newman.options import NewmanModelAdmin
from ella.newman import actions


class NewmanSite(AdminSite):
    norole_template = None
    index_template = 'newman/index.html'
    login_template = 'newman/login.html'
    app_index_template = 'newman/app_index.html'

    def __init__(self, name=None):
        super(NewmanSite, self).__init__(name=name)
        self._actions = {'delete_selected': actions.delete_selected}
        self._global_actions = self._actions.copy()

    def append_inline(self, to_models=(), inline=None):
        """
        Dynamic append inline to model admin options.
        """
        for s in to_models:
            app_name, model_name = s.split('.')
            model = models.get_model(app_name, model_name)
            if model in self._registry.keys():
                opts_class = self._registry[model].__class__
                opts_class.inlines.append(inline)
                self.unregister(model)
                self.register(model, opts_class)

    def register(self, model_or_iterable, admin_class=None, **options):
        """
        If an admin class isn't given, it will use NewmanModelAdmin.
        """
        if not admin_class:
            admin_class = NewmanModelAdmin

        super(NewmanSite, self).register(model_or_iterable, admin_class, **options)


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
            url(r'^%s/$' % NEWMAN_URL_PREFIX,
                wrap(self.newman_index),
                name="newman-index"),
            url(r'^%s/editor-box/$' % NEWMAN_URL_PREFIX,
                wrap(self.editor_box_view),
                name="newman-editor-box"),
            url(r'^%s/render-chunk/$' % NEWMAN_URL_PREFIX,
                wrap(self.render_chunk_template_view),
                name="newman-render-chunk"),
        )

        if 'djangomarkup' in settings.INSTALLED_APPS:
            urlpatterns += patterns('',
                url(r'^%s/editor-preview/$' % NEWMAN_URL_PREFIX,
                    'djangomarkup.views.transform',
                    name="djangomarkup-preview"),
            )

        urlpatterns += super(NewmanSite, self).get_urls()
        return urlpatterns

    @require_AJAX
    def render_chunk_template_view(self, request, extra_context=None):
        """
        Render template snippet defined in GET parameter 'chunk'
        """

        context = template.RequestContext(request)

        tpl = request.GET.get('chunk', None)

        if not tpl:
            raise Http404

        template_path = "newman/chunks/%s.html" % tpl

        return render_to_response(template_path, context,
            context_instance=template.RequestContext(request)
        )

#    @require_AJAX
    def editor_box_view(self, request, extra_context=None):
        """
        Render template with editor box form
        """
        context = {
            'boxform': EditorBoxForm()
        }
        return render_to_response('newman/widget/editor_box.html', context,
            context_instance=template.RequestContext(request)
        )

    @never_cache
    def login(self, request):
        """
        Displays the login form for the given HttpRequest.
        """
        from django.contrib.auth.models import User

        ERROR_MESSAGE = _("Please enter a correct username and password. Note that both fields are case-sensitive.")
        LOGIN_FORM_KEY = 'this_is_the_login_form'

        # If this isn't already the login page, display it.
        if not request.POST.has_key(LOGIN_FORM_KEY):
            if request.POST:
                message = _("Please log in again, because your session has expired.")
            else:
                message = ""
            return self.display_login_form(request, message)

        # Check that the user accepts cookies.
        if not request.session.test_cookie_worked():
            message = _("Looks like your browser isn't configured to accept cookies. Please enable cookies, reload this page, and try again.")
            return self.display_login_form(request, message)
        else:
            request.session.delete_test_cookie()

        # Check the password.
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        user = authenticate(username=username, password=password)
        if user is None:
            message = ERROR_MESSAGE
            if u'@' in username:
                # Mistakenly entered e-mail address instead of username? Look it up.
                try:
                    user = User.objects.get(email=username)
                except (User.DoesNotExist, User.MultipleObjectsReturned):
                    message = _("Usernames cannot contain the '@' character.")
                else:
                    if user.check_password(password):
                        message = _("Your e-mail address is not your username."
                                    " Try '%s' instead.") % user.username
                    else:
                        message = _("Usernames cannot contain the '@' character.")
            return self.display_login_form(request, message)

        # The user data is correct; log in the user in and continue.
        else:
            if user.is_active and user.is_staff:
                login(request, user)
                # user has no applicable categories, probably his role is undefined
                if not applicable_categories(user) and not user.is_superuser:
                    return self.norole(request, user)

                next_path = request.get_full_path()

                # load all user's specific settings into session
                for c in AdminSetting.objects.filter(user=user).values('var'):
                    uc = get_user_config(user, c['var'])
                    set_user_config_session(request.session, c['var'], uc)

                if request.POST.get('next'):
                    next_path += request.POST.get('next')
                return HttpResponseRedirect(next_path)
            else:
                return self.display_login_form(request, ERROR_MESSAGE)

    def norole(self, request, user):
        context = {
            'title': _('Site administration'),
            'user': user,
        }
        logout(request)
        return render_to_response(
            self.norole_template or 'newman/error_norole.html',
            context,
            context_instance=template.RequestContext(request)
        )

    def newman_index(self, request, extra_context=None):
        """
        Displays the main Newman index page, without installed apps.
        """
        data = {'sites': []}
        try:
            data['sites'] = get_user_config(request.user, CATEGORY_FILTER)
        except KeyError:
            data['sites'] = []

        publishable_lookup_fields = {
            'day': 'publish_from__day',
            'month': 'publish_from__month',
            'year': 'publish_from__year'
        }
        site_filter_form = SiteFilterForm(data=data, user=request.user)
        cts = []
        last_filters = {}
        for model, model_admin in self._registry.items():
            if has_model_list_permission(request.user, model) and model_admin.search_fields:
                ct = ContentType.objects.get_for_model(model)
                cts.append(ct)
                # Load saved filter configurations for changelists
                key = 'filter__%s__%s' % (ct.app_label, ct.model)
                last_filter = AdminSetting.objects.filter(var=key, user=request.user)
                if last_filter:
                    last_filters[key] = '?%s' % json_decode(last_filter[0].value)

        future_qs = Placement.objects.select_related().filter(publish_from__gt=datetime.datetime.now())
        future_qs_perm = permission_filtered_model_qs(future_qs, request.user)
        future_placements = user_category_filter(future_qs_perm, request.user)

        context = {
            'title': _('Site administration'),
            'site_filter_form': site_filter_form,
            'searchable_content_types': cts,
            'last_filters': last_filters,
            'future_placements': future_placements,
            'publishable_lookup_fields': publishable_lookup_fields
        }
        context.update(extra_context or {})
        return render_to_response('newman/newman-index.html', context,
            context_instance=template.RequestContext(request)
        )

    @require_AJAX
    def err_report(self, request, extra_context=None):
        """
        Sends error report or feature request to administrator.
        """

        form = ErrorReportForm(request.POST)
        if form.is_valid():
            try:
                e = EmailMessage('Newman report: %s' % form.cleaned_data['err_subject'], form.cleaned_data['err_message'],
                                 from_email=request.user.email, to=settings.ERR_REPORT_RECIPIENTS)
                e.send()
                return JsonResponse(ugettext('Your report was sent.'))
            except:
                return JsonResponseError(ugettext('SMTP error.'), status=STATUS_SMTP_ERROR)
        else:
            error_dict = {}
            for e in form.errors:
                error_dict[u"id_%s" % e] = [ u"%s" % ee for ee in form.errors[e] ]
            return JsonResponse(ugettext('Subject or message is empty.'), errors=error_dict, status=STATUS_FORM_ERROR)

    @require_AJAX
    def cat_filters_save(self, request, extra_content=None):

        site_filter_form = SiteFilterForm(user=request.user, data=request.POST)
        if site_filter_form.is_valid():
            set_user_config_db(request.user, CATEGORY_FILTER, site_filter_form.cleaned_data['sites'])
            set_user_config_session(request.session, CATEGORY_FILTER, site_filter_form.cleaned_data['sites'])
            return JsonResponse(ugettext('Your settings were saved.'))
        else:
            return JsonResponseError(ugettext('Error in form.'), status=STATUS_FORM_ERROR)

    @property
    def applicable_content_types(self):

        acts = []
        cts = get_cached_list(ContentType)
        for ct in cts:
            if ct.model_class() and (issubclass(ct.model_class(), Publishable) or '%s.%s' % (ct.app_label, ct.model) in NON_PUBLISHABLE_CTS):
                acts.append(ct)

        return acts

site = NewmanSite(name="newman")
