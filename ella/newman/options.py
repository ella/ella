from django.core.exceptions import PermissionDenied
from django.conf import settings
from ella.ellaadmin.options import SUGGEST_VIEW_MIN_LENGTH, SUGGEST_VIEW_LIMIT,\
    SUGGEST_RETURN_ALL_FIELD

from django.contrib import admin
from django.contrib.admin import helpers
from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.options import IncorrectLookupParameters
from django import template
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.contrib.admin.views.main import ERROR_FLAG
from django.shortcuts import render_to_response
from django.db import transaction
from django.db.models import Q, query
from django.db.models.fields import FieldDoesNotExist
from django.utils.functional import update_wrapper
from django.utils.translation import ugettext as _
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

from ella.newman.changelist import NewmanChangeList, FilterChangeList
from ella.newman import models, fields
from django.contrib.admin.util import unquote
from django.forms.formsets import all_valid

DEFAULT_LIST_PER_PAGE = getattr(settings, 'NEWMAN_LIST_PER_PAGE', 25)

class NewmanModelAdmin(ModelAdmin):
    registered_views = []

    def __init__(self, *args, **kwargs):
        super(NewmanModelAdmin, self).__init__(*args, **kwargs)
        self.list_per_page = DEFAULT_LIST_PER_PAGE
        #NewmanModelAdmin.register(lambda x: x is None, self.changelist_view)
        #NewmanModelAdmin.register(lambda x: x.endswith('suggest'), self.suggest_view)
        #NewmanModelAdmin.register(lambda x: x.endswith('filters'), self.filters_view)

    def get_urls(self):

        from django.conf.urls.defaults import patterns, url

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.admin_site.name, self.model._meta.app_label, self.model._meta.module_name

        urlpatterns = patterns('',
            url(r'^suggest/$',
                wrap(self.suggest_view),
                name='%sadmin_%s_%s_suggest' % info),
            url(r'^filters/$',
                wrap(self.filters_view),
                name='%sadmin_%s_%s_filters' % info),
)
        urlpatterns += super(NewmanModelAdmin, self).get_urls()
        return urlpatterns

    def filters_view(self, request, extra_context=None):
        "stolen from: The 'change list' admin view for this model."
        opts = self.model._meta
        app_label = opts.app_label
        try:
            cl = FilterChangeList(request, self.model, self.list_display, self.list_display_links, self.list_filter,
                self.date_hierarchy, self.search_fields, self.list_select_related, self.list_per_page, self)
        except IncorrectLookupParameters:
            # Wacky lookup parameters were given, so redirect to the main
            # changelist page, without parameters, and pass an 'invalid=1'
            # parameter via the query string. If wacky parameters were given and
            # the 'invalid=1' parameter was already in the query string, something
            # is screwed up with the database, so display an error page.
            if ERROR_FLAG in request.GET.keys():
                return render_to_response('admin/invalid_setup.html', {'title': _('Database error')})
            return HttpResponseRedirect(request.path + '?' + ERROR_FLAG + '=1')

        context = {
            'title': cl.title,
            'is_popup': cl.is_popup,
            'cl': cl,
            'has_add_permission': self.has_add_permission(request),
            'root_path': self.admin_site.root_path,
            'app_label': app_label,
}
        context.update(extra_context or {})
        out= render_to_response(
            'admin/filters.html',
            context,
            context_instance=template.RequestContext(request)
)
        return HttpResponse(out, mimetype='text/plain;charset=utf-8')


    def changelist_view(self, request, extra_context=None):
        # accepts only ajax calls if not DEBUG
        if not request.is_ajax() and not settings.DEBUG:
            raise Http404

        opts = self.model._meta
        app_label = opts.app_label
        if not self.has_change_permission(request, None):
            raise PermissionDenied # commented out as user is restricted by category
        try:
            cl = NewmanChangeList(request, self.model, self.list_display, self.list_display_links, self.list_filter,
                self.date_hierarchy, self.search_fields, self.list_select_related, self.list_per_page, self)
        except IncorrectLookupParameters:
            # Wacky lookup parameters were given, so redirect to the main
            # changelist page, without parameters, and pass an 'invalid=1'
            # parameter via the query string. If wacky parameters were given and
            # the 'invalid=1' parameter was already in the query string, something
            # is screwed up with the database, so display an error page.
            if ERROR_FLAG in request.GET.keys():
                return render_to_response('admin/invalid_setup.html', {'title': _('Database error')})
            return HttpResponseRedirect(request.path + '?' + ERROR_FLAG + '=1')

        context = {
            'title': cl.title,
            'is_popup': cl.is_popup,
            'cl': cl,
            'has_add_permission': self.has_add_permission(request),
            'root_path': self.admin_site.root_path,
            'app_label': app_label,
}
        context.update(extra_context or {})
        return render_to_response(self.change_list_template or [
            'admin/%s/%s/change_list.html' % (app_label, opts.object_name.lower()),
            'admin/%s/change_list.html' % app_label,
            'admin/change_list.html'
        ], context, context_instance=template.RequestContext(request))


    def suggest_view(self, request, extra_context=None):
        # accepts only ajax calls if not DEBUG
        if not request.is_ajax() and not settings.DEBUG:
            raise Http404

        if not ('f' in request.GET.keys() and 'q' in request.GET.keys()):
            raise AttributeError, 'Invalid query attributes. Example: ".../?f=field_a&f=field_b&q=search_term&o=offset"'
        elif len(request.GET.get('q')) < SUGGEST_VIEW_MIN_LENGTH:
            return HttpResponse('', mimetype='text/plain;charset=utf-8')

        offset = 0
        if 'o' in request.GET.keys() and request.GET.get('o'):
            offset = int(request.GET.get('o'))
        limit = offset + SUGGEST_VIEW_LIMIT

        lookup_fields = [u'id'] + request.GET.getlist('f')
        lookup_value = request.GET.get('q')
        lookup = None

        model_fields = [f.name for f in self.model._meta.fields]

        for f in lookup_fields:

            if not (f in model_fields or f.split('__')[0] in model_fields):
                raise AttributeError, 'Model "%s" has not field "%s". Possible fields are "%s".' \
                                    % (self.model._meta.object_name, f, ', '.join(model_fields))
            lookup_key = str('%s__icontains' % f)
            if not lookup:
                lookup = Q(**{lookup_key: lookup_value})
            else:
                lookup = lookup | Q(**{lookup_key: lookup_value})

        if SUGGEST_RETURN_ALL_FIELD:
            data = self.model.objects.filter(lookup).values(*lookup_fields)
        else:
            data = self.model.objects.filter(lookup).values(*lookup_fields[:2])

        cnt = len(data)

        # sort the suggested items so that those starting with the sought term come first
        def compare(a,b):
            def _cmp(a,b,sought):
                a_starts = unicode(a).lower().startswith(sought)
                b_starts = unicode(b).lower().startswith(sought)
                # if exactly one of (a,b) starts with sought, the one starting with it comes first
                if a_starts ^ b_starts:
                    if a_starts: return -1
                    if b_starts: return +1
                # else compare lexicographically
                return cmp(a,b)
            return _cmp(a,b,unicode(lookup_value).lower())
        data = list(data)
        if offset >= len(data): return HttpResponse('SPECIAL: OFFSET OUT OF RANGE', mimetype='text/plain')
        data.sort(cmp=compare, key=lambda x: x[lookup_fields[1]])
        data = data[offset:limit]

        ft = []
        ft.append('{cnt:%d}' % cnt)
        for item in data:
            if SUGGEST_RETURN_ALL_FIELD:
                ft.append("%s".encode('utf-8') % '|'.join("%s" % item[f] for f in lookup_fields))
            else:
                ft.append("%s".encode('utf-8') % '|'.join("%s" % item[f] for f in lookup_fields[:2]))

        return HttpResponse('\n'.join(ft), mimetype='text/plain;charset=utf-8')


    def queryset(self, request):
        """
        First semi-working draft of category-based permissions. It will allow permissions to be set per category
        effectively hiding the content the user has no permission to see/change.
        """
        if request.user.is_superuser:
            return super(NewmanModelAdmin, self).queryset(request)
        q = admin.ModelAdmin.queryset(self, request)

        view_perm = self.opts.app_label + '.' + 'view_' + self.model._meta.module_name.lower()
        change_perm = self.opts.app_label + '.' + 'change_' + self.model._meta.module_name.lower()
        try:
            self.model._meta.get_field('category')
            categories = models.applicable_categories(request.user, view_perm) + models.applicable_categories(request.user, change_perm)

            if categories:
                # TODO: terrible hack for circumventing invalid Q(__in=[]) | Q(__in=[])
                q = q.filter(Q(category__in=categories))
            else:
                q = query.EmptyQuerySet()
        except FieldDoesNotExist:
            pass
        return q

    def has_view_permission(self, request, obj):
        opts = self.opts
        view_perm = '%s.view_%s' % (opts.app_label, opts.object_name.lower())
        return request.user.has_perm(view_perm)

    def has_model_view_permission(self, request, obj=None):
        """ returns True if user has permission to view this model, otherwise False. """
        # try to find view or change perm. for given user in his permissions or groups permissions
        can_change = admin.ModelAdmin.has_change_permission(self, request, obj)
        can_view = self.has_view_permission(request, obj)
        if can_view or can_change:
            return True

        # find permission to view or change in CategoryUserRoles for given user
        user = request.user
        opts = self.opts
        change_perm = '%s.%s' % (opts.app_label, opts.get_change_permission())
        view_perm = '%s.view_%s' % (opts.app_label, opts.object_name.lower())
        perms = [change_perm, view_perm]
        for role in user.categoryuserrole_set.all():
            for perm in role.group.permissions.all():
                p = '%s.%s' % (opts.app_label, perm.codename)
                if p in perms:
                    return True
        # no permission found
        return False

    def has_change_permission(self, request, obj=None):
        """
        Returns True if the given request has permission to change the given
        Django model instance.

        If `obj` is None, this should return True if the given request has
        permission to change *any* object of the given type.

        If request is GET type, at least view_permission is needed. In case
        of POST request change permission is needed.
        """
        if obj is None or not hasattr(obj, 'category'):
            if request.method == 'POST':
                return admin.ModelAdmin.has_change_permission(self, request, obj)
            else:
                return self.has_model_view_permission(request, obj)

        opts = self.opts
        change_perm = '%s.%s' % (opts.app_label, opts.get_change_permission())
        view_perm = '%s.view_%s' % (opts.app_label, opts.object_name.lower())
        can_view = models.has_category_permission(request.user, obj, obj.category, view_perm)
        can_change = models.has_category_permission(request.user, obj, obj.category, change_perm)

        if request.method == 'POST' and can_change:
            return True
        elif request.method == 'GET' and (can_view or can_change):
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Returns True if the given request has permission to change the given
        Django model instance.

        If `obj` is None, this should return True if the given request has
        permission to delete *any* object of the given type.
        """
        opts = self.opts
        del_perm = opts.app_label + '.' + opts.get_delete_permission()
        if request.user.has_perm(del_perm):
            return True
        user = request.user
        for role in user.categoryuserrole_set.all():
            if del_perm in role.group.permissions.all():
                return True
        # no permission found
        return False

    def change_view(self, request, object_id, extra_context=None):
        "The 'change' admin view for this model."
        model = self.model
        opts = model._meta

        try:
            obj = model._default_manager.get(pk=unquote(object_id))
        except model.DoesNotExist:
            # Don't raise Http404 just yet, because we haven't checked
            # permissions yet. We don't want an unauthenticated user to be able
            # to determine whether a given object exists.
            obj = None

        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        if obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {'name': force_unicode(opts.verbose_name), 'key': escape(object_id)})

        if request.method == 'POST' and request.POST.has_key("_saveasnew"):
            return self.add_view(request, form_url='../../add/')

        ModelForm = self.get_form(request, obj)
        formsets = []
        if request.method == 'POST':
            form = ModelForm(request.POST, request.FILES, instance=obj)
            if form.is_valid():
                form_validated = True
                new_object = self.save_form(request, form, change=True)
            else:
                form_validated = False
                new_object = obj
            for FormSet in self.get_formsets(request, new_object):
                formset = FormSet(request.POST, request.FILES,
                                  instance=new_object)
                formsets.append(formset)

            if all_valid(formsets) and form_validated:
                self.save_model(request, new_object, form, change=True)
                form.save_m2m()
                for formset in formsets:
                    self.save_formset(request, form, formset, change=True)

                change_message = self.construct_change_message(request, form, formsets)
                self.log_change(request, new_object, change_message)
                return self.response_change(request, new_object)

        else:
            form = ModelForm(instance=obj)
            for FormSet in self.get_formsets(request, obj):
                formset = FormSet(instance=obj)
                formsets.append(formset)

        adminForm = helpers.AdminForm(form, self.get_fieldsets(request, obj), self.prepopulated_fields)
        media = self.media + adminForm.media

        inline_admin_formsets = []
        for inline, formset in zip(self.inline_instances, formsets):
            fieldsets = list(inline.get_fieldsets(request, obj))
            inline_admin_formset = helpers.InlineAdminFormSet(inline, formset, fieldsets)
            inline_admin_formsets.append(inline_admin_formset)
            media = media + inline_admin_formset.media

        # raw media paths for ajax implementation
        raw_media = []
        raw_media.extend(media._css['screen'])
        raw_media.extend(media._js)

        context = {
            'title': _('Change %s') % force_unicode(opts.verbose_name),
            'adminform': adminForm,
            'object_id': object_id,
            'original': obj,
            'is_popup': request.REQUEST.has_key('_popup'),
            'media': raw_media,
            'inline_admin_formsets': inline_admin_formsets,
            'errors': helpers.AdminErrorList(form, formsets),
            'root_path': self.admin_site.root_path,
            'app_label': opts.app_label,
}
        context.update(extra_context or {})
        return self.render_change_form(request, context, change=True, obj=obj)
    change_view = transaction.commit_on_success(change_view)

    def formfield_for_dbfield(self, db_field, **kwargs):

        # TODO: Only hotfix for django 9791+
        if 'request' in kwargs:
            del kwargs['request']

        for css_class, rich_text_fields in getattr(self, 'rich_text_fields', {}).iteritems():
            if db_field.name in rich_text_fields:
                kwargs.update({
                    'required': not db_field.blank,
                    'label': db_field.verbose_name,
})
                rich_text_field = fields.RichTextAreaField(**kwargs)
                if css_class:
                    rich_text_field.widget.attrs['class'] += ' %s' % css_class
                return rich_text_field

        return super(NewmanModelAdmin, self).formfield_for_dbfield(db_field, **kwargs)

