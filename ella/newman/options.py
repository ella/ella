from django.core.exceptions import PermissionDenied
from django.conf import settings

from django.contrib import admin
from django.contrib.admin.options import InlineModelAdmin, IncorrectLookupParameters
from django.forms.models import BaseInlineFormSet
from django.forms.util import ErrorList
from django import template
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.contrib.admin.views.main import ERROR_FLAG
from django.shortcuts import render_to_response
from django.db import transaction
from django.db.models import Q
from django.utils.functional import update_wrapper
from django.utils.translation import ugettext as _
from django.utils.encoding import force_unicode

from django.contrib.admin.util import unquote
from django.forms.formsets import all_valid
from django.contrib.contenttypes.models import ContentType
from django.db.models.fields.related import ForeignKey, ManyToManyField


from ella.newman.changelist import NewmanChangeList, FilterChangeList
from ella.newman import models, fields, widgets
from ella.newman.decorators import require_AJAX

DEFAULT_LIST_PER_PAGE = getattr(settings, 'NEWMAN_LIST_PER_PAGE', 25)

def get_permission(permission_name, instance):
    return instance._meta.app_label + '.' + '%s_' % permission_name + instance._meta.module_name.lower()

def formfield_for_dbfield_factory(cls, db_field, **kwargs):

    if 'request' in kwargs:
        request = kwargs.pop('request', None)
        user = request.user

    for css_class, rich_text_fields in getattr(cls, 'rich_text_fields', {}).iteritems():
        if db_field.name in rich_text_fields:
            kwargs.update({
                'required': not db_field.blank,
                'label': db_field.verbose_name,
            })
            rich_text_field = fields.RichTextField(**kwargs)
            if css_class:
                rich_text_field.widget.attrs['class'] += ' %s' % css_class
            return rich_text_field

    if db_field.name in cls.raw_id_fields and isinstance(db_field, ForeignKey):
        kwargs['widget'] = widgets.ForeignKeyRawIdWidget(db_field.rel)
        return db_field.formfield(**kwargs)

    if db_field.name in getattr(cls, 'suggest_fields', {}).keys() \
                        and isinstance(db_field, (ForeignKey, ManyToManyField)):
        kwargs.update({
            'required': not db_field.blank,
            'label': db_field.verbose_name,
            'model': cls.model,
            'lookup': cls.suggest_fields[db_field.name]
        })
        print db_field.name
        return fields.AdminSuggestField(db_field, **kwargs)

    return db_field.formfield(**kwargs)


class NewmanModelAdmin(admin.ModelAdmin):

    def __init__(self, *args, **kwargs):
        super(NewmanModelAdmin, self).__init__(*args, **kwargs)
        self.list_per_page = DEFAULT_LIST_PER_PAGE

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
            url(r'^(.+)/draft/save/$',
                wrap(self.save_draft_view),
                name='%sadmin_%s_%s_save_draft' % info),
        )
        urlpatterns += super(NewmanModelAdmin, self).get_urls()
        return urlpatterns

    @require_AJAX
    def save_draft_view(self, request, extra_context=None):
        "Autosave data or save as (named) template"
        from ella.newman.models import AdminUserDraft

        ct = ContentType.objects.get_for_model(self.model)

        # TODO: clean old autosaved...

        AdminUserDraft.objects.create(
            ct = ct,
            user = request.user,
            data = request.POST.get('data')
        )

        return HttpResponse(content=_('Model data was saved'), mimetype='text/plain')

    @require_AJAX
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

    @require_AJAX
    def changelist_view(self, request, extra_context=None):

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

    @require_AJAX
    def suggest_view(self, request, extra_context=None):

        SUGGEST_VIEW_LIMIT = getattr(settings, 'SUGGEST_VIEW_LIMIT', 20)
        SUGGEST_VIEW_MIN_LENGTH = getattr(settings, 'SUGGEST_VIEW_MIN_LENGTH', 2)
        SUGGEST_RETURN_ALL_FIELD = getattr(settings, 'SUGGEST_RETURN_ALL_FIELD', True)

        if not ('f' in request.GET.keys() and 'q' in request.GET.keys()):
            raise AttributeError, 'Invalid query attributes. Example: ".../?f=field_a&f=field_b&q=search_term&o=offset"'
        elif len(request.GET.get('q')) < SUGGEST_VIEW_MIN_LENGTH:
            return HttpResponse( '', mimetype='text/plain;charset=utf-8' )

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
                ft.append( "%s".encode('utf-8') % '|'.join("%s" % item[f] for f in lookup_fields) )
            else:
                ft.append( "%s".encode('utf-8') % '|'.join("%s" % item[f] for f in lookup_fields[:2]) )

        return HttpResponse( '\n'.join(ft), mimetype='text/plain;charset=utf-8' )

    def has_view_permission(self, request, obj):
        opts = self.opts
        view_perm = '%s.view_%s' % ( opts.app_label, opts.object_name.lower() )
        return request.user.has_perm(view_perm)

    def has_model_view_permission(self, request, obj=None):
        """ returns True if user has permission to view this model, otherwise False. """
        # try to find view or change perm. for given user in his permissions or groups permissions
        can_change = admin.ModelAdmin.has_change_permission( self, request, obj )
        can_view = self.has_view_permission(request, obj)
        if can_view or can_change:
            return True

        # find permission to view or change in CategoryUserRoles for given user
        user = request.user
        opts = self.opts
        change_perm = '%s.%s' % ( opts.app_label, opts.get_change_permission() )
        view_perm = '%s.view_%s' % ( opts.app_label, opts.object_name.lower() )
        perms = [change_perm, view_perm]
        for role in user.categoryuserrole_set.all():
            for perm in role.group.permissions.all():
                p = '%s.%s' % ( opts.app_label, perm.codename )
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
        cfield = models.model_category_fk_value(obj)
        if obj is None or not cfield:
            if request.method == 'POST':
                return admin.ModelAdmin.has_change_permission( self, request, obj )
            else:
                return self.has_model_view_permission(request, obj)

        opts = self.opts
        change_perm = '%s.%s' % ( opts.app_label, opts.get_change_permission() )
        view_perm = '%s.view_%s' % ( opts.app_label, opts.object_name.lower() )
        can_view = models.has_category_permission( request.user, cfield, view_perm )
        can_change = models.has_category_permission( request.user, cfield, change_perm )

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

    @require_AJAX
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

        adminForm = admin.helpers.AdminForm(form, self.get_fieldsets(request, obj), self.prepopulated_fields)
        media = self.media + adminForm.media

        inline_admin_formsets = []
        raw_inlines = {}
        for inline, formset in zip(self.inline_instances, formsets):
            # TODO: has user permission for inline model?
            #if request.user.has_module_perms(inline.model._meta.app_label):
            raw_inlines[str(inline.model._meta).replace('.', '__')] = formset
            fieldsets = list(inline.get_fieldsets(request, obj))
            inline_admin_formset = admin.helpers.InlineAdminFormSet(inline, formset, fieldsets)
            inline_admin_formsets.append(inline_admin_formset)
            media = media + inline_admin_formset.media

        # raw media paths for ajax implementation
        raw_media = []
        if media._css.has_key('screen'):
            raw_media.extend(media._css['screen'])
        raw_media.extend(media._js)

        raw_frm_all = {
            'form': form,
            'inlines': raw_inlines
        }

        context = {
            'title': _('Change %s') % force_unicode(opts.verbose_name),
            'adminform': adminForm,
            'raw_form': raw_frm_all,
            'object_id': object_id,
            'original': obj,
            'is_popup': request.REQUEST.has_key('_popup'),
            'media': raw_media,
            'inline_admin_formsets': inline_admin_formsets,
            'errors': admin.helpers.AdminErrorList(form, formsets),
            'root_path': self.admin_site.root_path,
            'app_label': opts.app_label,
        }
        context.update(extra_context or {})
        return self.render_change_form(request, context, change=True, obj=obj)
    change_view = transaction.commit_on_success(change_view)

    def restrict_field_categories(self, db_field, user, model):
        f = db_field
        if hasattr(f.queryset, '_newman_filtered'):
            return
        view_perm = get_permission('view', model)
        change_perm = get_permission('change', model)
        perms = (view_perm, change_perm,)
        qs = models.permission_filtered_model_qs(f.queryset, self.model, user, perms)
        qs._newman_filtered = True #magic variable
        f._set_queryset(qs)

    def formfield_for_dbfield(self, db_field, **kwargs):
        return formfield_for_dbfield_factory(self, db_field, **kwargs)

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
        perms = (view_perm, change_perm,)
        qs = models.permission_filtered_model_qs(q, self.model, request.user, perms)
        return qs

class NewmanInlineFormSet(BaseInlineFormSet):
    def get_queryset(self):
        user = self.form._magic_user
        if not hasattr(self, '_queryset'):
            if self.queryset is not None:
                qs = self.queryset
            else:
                qs = self.model._default_manager.get_query_set()
            # category base permissions
            if not user.is_superuser:
                for db_field in self.model._meta.fields:
                    if not models.is_category_fk(db_field):
                        continue
                    view_perm = get_permission('view', self.instance)
                    change_perm = get_permission('change', self.instance)
                    perms = (view_perm, change_perm,)
                    qs = models.permission_filtered_model_qs(qs, self.model, user, perms)

            if self.max_num > 0:
                self._queryset = qs[:self.max_num]
            else:
                self._queryset = qs
        return self._queryset

class NewmanInlineModelAdmin(InlineModelAdmin):
    formset = NewmanInlineFormSet

    def formfield_for_dbfield(self, db_field, **kwargs):
        return formfield_for_dbfield_factory(self, db_field, **kwargs)

    def get_formset(self, request, obj=None):
        setattr(self.form, '_magic_user', request.user) # prasarna
        return super(NewmanInlineModelAdmin, self).get_formset(request, obj)

class NewmanStackedInline(NewmanInlineModelAdmin):
    template = 'admin/edit_inline/stacked.html'

class NewmanTabularInline(NewmanInlineModelAdmin):
    template = 'admin/edit_inline/tabular.html'

# ------------------------------------
# Generics
# ------------------------------------

from django.forms.models import BaseModelFormSet, modelformset_factory, save_instance
from django.contrib.admin.options import flatten_fieldsets
from django.contrib.contenttypes.generic import generic_inlineformset_factory, \
    BaseGenericInlineFormSet as DJBaseGenericInlineFormSet
from django.forms.formsets import DELETION_FIELD_NAME

class BaseGenericInlineFormSet(DJBaseGenericInlineFormSet):
    """
    A formset for generic inline objects to a parent.
    """
    ct_field_name = "content_type"
    ct_fk_field_name = "object_id"

    def __init__(self, data=None, files=None, instance=None, save_as_new=None):
        super(BaseGenericInlineFormSet, self).__init__(
            data, files, instance, save_as_new
        )

    def get_queryset(self):
        # Avoid a circular import.
        from django.contrib.contenttypes.models import ContentType
        user = self.form._magic_user
        if self.instance is None:
            return self.model._default_manager.empty()
        out = self.model._default_manager.filter(**{
            self.ct_field.name: ContentType.objects.get_for_model(self.instance),
            self.ct_fk_field.name: self.instance.pk,
        })
        if user.is_superuser:
            return out
        # filtering -- view permitted categories only
        cfield = models.model_category_fk_value(self.model)
        if not cfield:
            return out
        view_perm = get_permission('view', self.instance)
        change_perm = get_permission('change', self.instance)
        perms = (view_perm, change_perm,)
        qs = models.permission_filtered_model_qs(out, self.model, user, perms)
        return qs

    def full_clean(self):
        super(BaseGenericInlineFormSet, self).full_clean()
        cfield = models.model_category_fk(self.instance)
        if not cfield:
            return
        cat = models.model_category_fk_value(self.instance)

        # next part is category-based permissions (only for objects with category field)
        def add_field_error(form, field_name, message):
                err_list = ErrorList( (message,) )
                form._errors[field_name] = err_list
        user = self.form._magic_user

        # Adding new object
        for form in self.extra_forms:
            if not form.has_changed():
                continue
            if cfield.name not in form.changed_data:
                continue
            add_perm = get_permission('add', form.instance)
            if not models.has_object_permission(user, form.instance, change_perm):
                self._non_form_errors = _('Creating objects is not permitted.')
                continue
            c = form.cleaned_data[cfield.name]
            if not models.has_category_permission(user, c, add_perm):
                add_field_error( form, cfield.name, _('Category not permitted') )

        # Changing existing object
        for form in self.initial_forms:
            change_perm = get_permission('change', form.instance)
            delete_perm = get_permission('delete', form.instance)
            if self.can_delete and form.cleaned_data[DELETION_FIELD_NAME]:
                if not models.has_object_permission(user, form.instance, delete_perm):
                    self._non_form_errors = _('Object deletion is not permitted.')
                    continue
                if not models.has_category_permission(user, form.instance.category, delete_perm):
                    self._non_form_errors = _('Object deletion is not permitted.')
                    continue
            if cfield.name not in form.changed_data:
                continue
            if not models.has_object_permission(user, form.instance, change_perm):
                self._non_form_errors = _('Object change is not permitted.')
                continue
            c = form.cleaned_data[cfield.name]
            if not models.has_category_permission(user, c, change_perm):
                add_field_error( form, cfield.name, _('Category not permitted') )
        #err_list = ErrorList( (u'Nepovolena kategorie',) )
        #self.initial_forms[1]._errors['category'] = err_list
        #del self.initial_forms[1].cleaned_data['category'] #pozor, lze mazat jen kdyz byl tento sloupec opravdu zmenen.
        #self._errors.append(
        # self.initial_form[1].instance  # konkretni placement
        # self.initial_form[1].changed_data  #seznam zmenenych fieldu
        # self.form.base_fields['category'].queryset

    def restrict_field_categories(self, form, user, model):
        if 'category' not in form.base_fields:
            return
        f = form.base_fields['category']
        if hasattr(f.queryset, '_newman_filtered'):
            return
        view_perm = get_permission('view', model)
        change_perm = get_permission('change', model)
        perms = (view_perm, change_perm,)
        qs = models.permission_filtered_model_qs(f.queryset, self.model, user, perms)
        qs._newman_filtered = True #magic variable
        f._set_queryset(qs)

    def _construct_form(self, i, **kwargs):
        if i < self._initial_form_count:
            qs = self.get_queryset()[i]
            kwargs['instance'] = qs
        user = self.form._magic_user
        self.restrict_field_categories(self.form, user, self.model)
        return super(BaseModelFormSet, self)._construct_form(i, **kwargs)



class GenericInlineModelAdmin(NewmanInlineModelAdmin):
    ct_field = "content_type"
    ct_fk_field = "object_id"
    formset = BaseGenericInlineFormSet

    def __init__(self, *args, **kwargs):
        super(GenericInlineModelAdmin, self).__init__(*args, **kwargs)

    def get_formset(self, request, obj=None):
        setattr(self.form, '_magic_user', request.user) # prasarna
        if self.declared_fieldsets:
            fields = flatten_fieldsets(self.declared_fieldsets)
        else:
            fields = None
        defaults = {
            "ct_field": self.ct_field,
            "fk_field": self.ct_fk_field,
            "form": self.form,
            "formfield_callback": self.formfield_for_dbfield,
            "formset": self.formset,
            "extra": self.extra,
            "max_num": self.max_num,
            "can_delete": True,
            "can_order": False,
            "fields": fields,
        }
        self.user = request.user
        return generic_inlineformset_factory(self.model, **defaults)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if models.is_category_fk(db_field):
            fld = super(GenericInlineModelAdmin, self).formfield_for_dbfield(db_field, **kwargs)#FIXME get fld.queryset different way
            kwargs.update({
                'model': self.model,
                'user': self.user
            })
            return fields.CategoryChoiceField(fld.queryset, **kwargs)
        return formfield_for_dbfield_factory(self, db_field, **kwargs)

class GenericStackedInline(GenericInlineModelAdmin):
    template = 'admin/edit_inline/stacked.html'

class GenericTabularInline(GenericInlineModelAdmin):
    template = 'admin/edit_inline/tabular.html'
