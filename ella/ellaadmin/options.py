from django.utils.functional import memoize
from django.core.urlresolvers import reverse, NoReverseMatch
from django.shortcuts import render_to_response
from django import template
from django.db.models import ForeignKey, SlugField

from django.contrib import admin
from django.contrib.admin.options import flatten_fieldsets
from django import newforms as forms
from django.shortcuts import render_to_response
from django import http
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _

from ella.ellaadmin import widgets
from ella.core.middleware import get_current_request


def mixin_ella_admin(admin_class):
    if admin_class == admin.ModelAdmin:
        return ExtendedModelAdmin

    if EllaAdminOptionsMixin in admin_class.__bases__:
        return admin_class

    bases = list(admin_class.__bases__)
    admin_class.__bases__ = tuple([EllaAdminOptionsMixin] + bases)
    return admin_class

def register_ella_admin(func):
    def _register(self, model_or_iterable, admin_class=None, **options):
        admin_class = admin_class or admin.ModelAdmin
        admin_class = mixin_ella_admin(admin_class)
        for inline in admin_class.inlines:
            inline = mixin_ella_admin(inline)
        return func(self, model_or_iterable, admin_class, **options)
    return _register


class EllaAdminSite(admin.AdminSite):
    def __init__(self):
        self._registry = admin.site._registry
        for options in self._registry.values():
            options.__class__ = mixin_ella_admin(options.__class__)
            for inline in options.inlines:
                inline = mixin_ella_admin(inline)
        admin.AdminSite.register = register_ella_admin(admin.AdminSite.register)

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

class EllaAdminOptionsMixin(object):
    def formfield_for_dbfield(self, db_field, **kwargs):
        if isinstance(db_field, SlugField):
            params = {
                'required': not db_field.blank,
                'max_length': db_field.max_length,
                'label': db_field.name,
                'error_message': _('Enter a valid slug.'),
}
            kwargs.update(params)
            return forms.RegexField('^[0-9a-z-]+$', **kwargs)

        elif db_field.name in ('target_ct', 'source_ct'):
            kwargs['widget'] = widgets.ContentTypeWidget

        elif db_field.name in ('target_id', 'source_id',):
            kwargs['widget'] = widgets.ForeignKeyRawIdWidget

        if isinstance(db_field, ForeignKey):
            if db_field.name in self.raw_id_fields:
                formfield = super(EllaAdminOptionsMixin, self).formfield_for_dbfield(db_field, **kwargs)
                formfield.widget.render = widgets.ExtendedRelatedFieldWidgetWrapper(formfield.widget.render, db_field.rel, self.admin_site)
                return formfield

        return super(EllaAdminOptionsMixin, self).formfield_for_dbfield(db_field, **kwargs)

class ExtendedModelAdmin(EllaAdminOptionsMixin, admin.ModelAdmin):
    pass

_admin_root_cache = {} # maps model to admin url
ADMIN_NAME = 'admin'
ADMIN_SCHEME = 'http'

def admin_root(model):
    """return admin list url"""
    try:
        root = '/%s' % reverse(ADMIN_NAME, args=['']).strip('/')
    except NoReverseMatch:
        try:
            root = '%s://%s' % (ADMIN_SCHEME, Site.objects.get(name=ADMIN_NAME).domain)
        except Site.DoesNotExist:
            root = '/%s' % ADMIN_NAME
    app_label = model._meta.app_label
    model_name = model._meta.module_name
    return '%s/%s/%s' % (root, app_label, model_name)
admin_root = memoize(admin_root, _admin_root_cache, 1)

def admin_url(obj):
    """return valid admin edit page url"""
    root = admin_root(obj.__class__)
    return '%s/%d/' % (root, obj._get_pk_val())


site = EllaAdminSite()



'''
class ContentTypeChoice(forms.ChoiceField):
    def clean(self, value):
        from django.contrib.contenttypes.models import ContentType
        value = super(ContentTypeChoice, self).clean(value)
        return ContentType.objects.get(pk=value)

class EllaAdminForm(forms.BaseForm):
    def clean(self):
        from ella.ellaadmin import models
        permission = self._model._meta.app_label + '.' + self.action + '_' + self._model._meta.module_name.lower()
        if 'category' in self.cleaned_data:
            print 'Found category ', self.cleaned_data['category'], permission
            if not models.has_category_permission(get_current_request().user, self._model, self.cleaned_data['category'], permission):
                raise forms.ValidationError, ugettext("You don't have permission to change an object in category %(category)s.") % self.cleaned_data['category']

        if 'site' in self.cleaned_data:
            if not models.has_site_permission(get_current_request().user, self._model, self.cleaned_data['site'], permission):
                raise forms.ValidationError, ugettext("You don't have permission to change an object in site %(site)s.") % self.cleaned_data['site']

        return self.cleaned_data

class EllaAdminEditForm(EllaAdminForm):
    action = 'change'

class EllaAdminAddForm(EllaAdminForm):
    action = 'add'

class EllaAdminOptionsMixin(EllaAdminOptionsMixin):
    """
    First semi-working draft of category-based permissions. It will allow permissions to be set per-site and per category
    effectively hiding the content the user has no permission to see/change.
    """

    def queryset(self, request):
        from ella.ellaadmin import models
        from django.db.models import Q, query
        from django.db.models.fields import FieldDoesNotExist
        q = admin.ModelAdmin.queryset(self, request)

        if request.user.is_superuser:
            return q

        view_perm = self.opts.app_label + '.' + 'view_' + self.model._meta.module_name.lower()
        change_perm = self.opts.app_label + '.' + 'change_' + self.model._meta.module_name.lower()
        sites = None

        try:
            self.model._meta.get_field('site')
            sites = models.applicable_sites(request.user, view_perm) + models.applicable_sites(request.user, change_perm)
            q = q.filter(site__in=sites)
        except FieldDoesNotExist:
            pass

        try:
            self.model._meta.get_field('category')
            if sites is None:
                sites = models.applicable_sites(request.user, view_perm) + models.applicable_sites(request.user, change_perm)
            categories = models.applicable_categories(request.user, view_perm) + models.applicable_categories(request.user, change_perm)

            if sites or categories:
                # TODO: terrible hack for circumventing invalid Q(__in=[]) | Q(__in=[])
                q = q.filter(Q(category__site__in=sites) | Q(category__in=categories))
            else:
                q = query.EmptyQuerySet()
        except FieldDoesNotExist:
            pass

        return q

    def has_change_permission(self, request, obj=None):
        """
        Returns True if the given request has permission to change the given
        Django model instance.

        If `obj` is None, this should return True if the given request has
        permission to change *any* object of the given type.
        """
        from ella.ellaadmin import models
        if obj is None or not hasattr(obj, 'category'):
            return admin.ModelAdmin.has_change_permission(self, request, obj)
        opts = self.opts
        return models.has_category_permission(request.user, obj, obj.category, opts.app_label + '.' + opts.get_change_permission())

    def form_add(self, request):
        """
        Returns a Form class for use in the admin add view.
        """
        if self.declared_fieldsets:
            fields = flatten_fieldsets(self.declared_fieldsets)
        else:
            fields = None
        return forms.form_for_model(self.model, fields=fields, formfield_callback=self.formfield_for_dbfield, form=EllaAdminAddForm)

    def form_change(self, request, obj):
        """
        Returns a Form class for use in the admin change view.
        """
        if self.declared_fieldsets:
            fields = flatten_fieldsets(self.declared_fieldsets)
        else:
            fields = None
        return forms.form_for_instance(obj, fields=fields, formfield_callback=self.formfield_for_dbfield, form=EllaAdminEditForm)

    #def formset_add(self, request):
    #    """Returns an InlineFormSet class for use in admin add views."""
    #    if self.declared_fieldsets:
    #        fields = flatten_fieldsets(self.declared_fieldsets)
    #    else:
    #        fields = None
    #    return forms.inline_formset(self.parent_model, self.model, fk_name=self.fk_name, fields=fields,
    #            formfield_callback=self.formfield_for_dbfield, extra=self.extra, formset=self.formset, form=EllaAdminAddForm)
    #
    #def formset_change(self, request, obj):
    #    """Returns an InlineFormSet class for use in admin change views."""
    #    if self.declared_fieldsets:
    #        fields = flatten_fieldsets(self.declared_fieldsets)
    #    else:
    #        fields = None
    #    return forms.inline_formset(self.parent_model, self.model, fk_name=self.fk_name, fields=fields,
    #        formfield_callback=self.formfield_for_dbfield, extra=self.extra, formset=self.formset, form=EllaAdminEditForm)
'''




