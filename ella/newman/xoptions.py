from django import template
from django.forms.formsets import all_valid
from django.contrib.admin import helpers
from django.contrib.admin.util import unquote
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.utils.translation import ngettext
from django.utils.encoding import force_unicode
try:
    set
except NameError:
    from sets import Set as set     # Python 2.3 fallback
from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.views.main import ChangeList, ERROR_FLAG

class XModelAdmin(ModelAdmin):
    """
    XModelAdmin class is intended as bridge (or adapter) between NewmanModelAdmin and django's ModelAdmin.
    Original ModelAdmin's views are unsuitable for Newman as they don't allow changing ChangeList
    classes per view, adding custom JS, CSS to views etc. Newman team is going to overload
    several methods of XModelAdmin rather than copypasting whole views of original ModelAdmin.
    """
    "Encapsulates all admin options and functionality for a given model."

    list_display = ('__str__',)
    list_display_links = ()
    list_filter = ()
    list_select_related = False
    list_per_page = 100
    list_editable = ()
    search_fields = ()
    date_hierarchy = None
    save_as = False
    save_on_top = False
    ordering = None
    inlines = []

    # Custom templates (designed to be over-ridden in subclasses)
    change_form_template = None
    change_list_template = None
    delete_confirmation_template = None
    object_history_template = None

    # ChangeList class for view
    changelist_view_cl = ChangeList

    def __init__(self, *args):
        super(XModelAdmin, self).__init__(*args)

    def get_change_view_formsets(self, request, obj):
        formsets = []
        ModelForm = self.get_form(request, obj)
        if request.method == 'POST':
            form = ModelForm(request.POST, request.FILES, instance=obj)
            if form.is_valid():
                form_validated = True
                new_object = self.save_form(request, form, change=True)
            else:
                form_validated = False
                new_object = obj
            prefixes = {}
            for FormSet in self.get_formsets(request, new_object):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                formset = FormSet(request.POST, request.FILES,
                                  instance=new_object, prefix=prefix)
                formsets.append(formset)

            if all_valid(formsets) and form_validated:
                self.save_model(request, new_object, form, change=True)
                form.save_m2m()
                for formset in formsets:
                    self.save_formset(request, form, formset, change=True)

                change_message = self.construct_change_message(request, form, formsets)
                self.log_change(request, new_object, change_message)
                return self.response_change(request, new_object), None

        else:
            form = ModelForm(instance=obj)
            prefixes = {}
            for FormSet in self.get_formsets(request, obj):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                formset = FormSet(instance=obj, prefix=prefix)
                formsets.append(formset)
        return formsets, form

    def get_change_view_inline_formsets(self, request, obj, formsets, media):
        inline_admin_formsets = []
        for inline, formset in zip(self.inline_instances, formsets):
            fieldsets = list(inline.get_fieldsets(request, obj))
            inline_admin_formset = helpers.InlineAdminFormSet(inline, formset, fieldsets)
            inline_admin_formsets.append(inline_admin_formset)
            media = media + inline_admin_formset.media
        return inline_admin_formsets, media

    def get_change_view_object(self, object_id):
        model = self.model
        opts = model._meta
        try:
            obj = model._default_manager.get(pk=unquote(object_id))
        except model.DoesNotExist:
            # Don't raise Http404 just yet, because we haven't checked
            # permissions yet. We don't want an unauthenticated user to be able
            # to determine whether a given object exists.
            obj = None
        return obj

    def get_change_view_context(self, request, object_id):
        model = self.model
        opts = model._meta
        obj = self.get_change_view_object(object_id)
        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        if obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {'name': force_unicode(opts.verbose_name), 'key': escape(object_id)})

        if request.method == 'POST' and request.POST.has_key("_saveasnew"):
            return self.add_view(request, form_url='../../add/')

        formsets, form = self.get_change_view_formsets(request, obj)
        if type(formsets) != list: #can return HttpResponseRedirect etc.
            return formsets
        adminForm = helpers.AdminForm(form, self.get_fieldsets(request, obj), self.prepopulated_fields)
        media = self.media + adminForm.media
        inline_admin_formsets, media = self.get_change_view_inline_formsets(request, obj, formsets, media)

        cx = {
            'title': _('Change %s') % force_unicode(opts.verbose_name),
            'adminform': adminForm,
            'object_id': object_id,
            'original': obj,
            'is_popup': request.REQUEST.has_key('_popup'),
            'media': media,
            'inline_admin_formsets': inline_admin_formsets,
            'errors': helpers.AdminErrorList(form, formsets),
            'root_path': self.admin_site.root_path,
            'app_label': opts.app_label,
        }
        # raw fields added
        cx['raw_form'] = form
        return cx

    def change_view(self, request, object_id, extra_context=None):
        "The 'change' admin view for this model."
        out = self.get_change_view_context(request, object_id)
        if type(out) != dict:
            # context is not a dict probably HttpReponseRedirect, or Http404 etc.
            return out
        context = out
        context.update(extra_context or {})
        obj = self.get_change_view_object(object_id)
        return self.render_change_form(request, context, change=True, obj=obj)
    change_view = transaction.commit_on_success(change_view)

    def get_changelist_context(self, request):
        opts = self.model._meta
        app_label = opts.app_label
        if not self.has_change_permission(request, None):
            raise PermissionDenied
        try:
            cl = self.changelist_view_cl(request, self.model, self.list_display, self.list_display_links, self.list_filter,
                self.date_hierarchy, self.search_fields, self.list_select_related, self.list_per_page, self.list_editable, self)
        except IncorrectLookupParameters:
            # Wacky lookup parameters were given, so redirect to the main
            # changelist page, without parameters, and pass an 'invalid=1'
            # parameter via the query string. If wacky parameters were given and
            # the 'invalid=1' parameter was already in the query string, something
            # is screwed up with the database, so display an error page.
            if ERROR_FLAG in request.GET.keys():
                return render_to_response('admin/invalid_setup.html', {'title': _('Database error')})
            return HttpResponseRedirect(request.path + '?' + ERROR_FLAG + '=1')

        # If the request was POSTed, this might be a bulk action or a bulk edit.
        # Try to look up an action first, but if this isn't an action the POST
        # will fall through to the bulk edit check, below.
        if request.method == 'POST':
            response = self.response_action(request, queryset=cl.get_query_set())
            if response:
                return response

        # If we're allowing changelist editing, we need to construct a formset
        # for the changelist given all the fields to be edited. Then we'll
        # use the formset to validate/process POSTed data.
        formset = cl.formset = None

        # Handle POSTed bulk-edit data.
        if request.method == "POST" and self.list_editable:
            FormSet = self.get_changelist_formset(request)
            formset = cl.formset = FormSet(request.POST, request.FILES, queryset=cl.result_list)
            if formset.is_valid():
                changecount = 0
                for form in formset.forms:
                    if form.has_changed():
                        obj = self.save_form(request, form, change=True)
                        self.save_model(request, obj, form, change=True)
                        form.save_m2m()
                        change_msg = self.construct_change_message(request, form, None)
                        self.log_change(request, obj, change_msg)
                        changecount += 1

                if changecount:
                    if changecount == 1:
                        name = force_unicode(opts.verbose_name)
                    else:
                        name = force_unicode(opts.verbose_name_plural)
                    msg = ngettext("%(count)s %(name)s was changed successfully.",
                                   "%(count)s %(name)s were changed successfully.",
                                   changecount) % {'count': changecount,
                                                   'name': name,
                                                   'obj': force_unicode(obj)}
                    self.message_user(request, msg)

                return HttpResponseRedirect(request.get_full_path())

        # Handle GET -- construct a formset for display.
        elif self.list_editable:
            FormSet = self.get_changelist_formset(request)
            formset = cl.formset = FormSet(queryset=cl.result_list)

        # Build the list of media to be used by the formset.
        if formset:
            media = self.media + formset.media
        else:
            media = None

        # Build the action form and populate it with available actions.
        action_form = self.action_form(auto_id=None)
        action_form.fields['action'].choices = self.get_action_choices(request)

        cx = {
            'title': cl.title,
            'is_popup': cl.is_popup,
            'cl': cl,
            'media': media,
            'has_add_permission': self.has_add_permission(request),
            'root_path': self.admin_site.root_path,
            'app_label': app_label,
            'action_form': action_form,
            'actions_on_top': self.actions_on_top,
            'actions_on_bottom': self.actions_on_bottom,
        }
        return cx

    def changelist_view(self, request, extra_context=None):
        "The 'change list' admin view for this model."
        opts = self.model._meta
        app_label = opts.app_label
        out = self.get_changelist_context(request)
        if type(out) != dict:
            return out
        context = out
        context.update(extra_context or {})
        return render_to_response(self.change_list_template or [
            'admin/%s/%s/change_list.html' % (app_label, opts.object_name.lower()),
            'admin/%s/change_list.html' % app_label,
            'admin/change_list.html'
        ], context, context_instance=template.RequestContext(request))

    def get_add_view_context(self, request, form_url):
        model = self.model
        opts = model._meta

        if not self.has_add_permission(request):
            raise PermissionDenied

        ModelForm = self.get_form(request)
        formsets = []
        context = {}
        if request.method == 'POST':
            form = ModelForm(request.POST, request.FILES)
            if form.is_valid():
                form_validated = True
                new_object = self.save_form(request, form, change=False)
            else:
                form_validated = False
                new_object = self.model()
            prefixes = {}
            for FormSet in self.get_formsets(request):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                formset = FormSet(data=request.POST, files=request.FILES,
                                  instance=new_object,
                                  save_as_new=request.POST.has_key("_saveasnew"),
                                  prefix=prefix)
                formsets.append(formset)
            if all_valid(formsets) and form_validated:
                self.save_model(request, new_object, form, change=False)
                form.save_m2m()
                for formset in formsets:
                    self.save_formset(request, form, formset, change=False)

                self.log_addition(request, new_object)
                self.response_add(request, new_object)
                context.update({
                    'object': new_object,
                    'object_added': True,
                })
        else:
            # Prepare the dict of initial data from the request.
            # We have to special-case M2Ms as a list of comma-separated PKs.
            initial = dict(request.GET.items())
            for k in initial:
                try:
                    f = opts.get_field(k)
                except models.FieldDoesNotExist:
                    continue
                if isinstance(f, models.ManyToManyField):
                    initial[k] = initial[k].split(",")
            form = ModelForm(initial=initial)
            prefixes = {}
            for FormSet in self.get_formsets(request):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                formset = FormSet(instance=self.model(), prefix=prefix)
                formsets.append(formset)

        adminForm = helpers.AdminForm(form, list(self.get_fieldsets(request)), self.prepopulated_fields)
        media = self.media + adminForm.media

        inline_admin_formsets = []
        for inline, formset in zip(self.inline_instances, formsets):
            fieldsets = list(inline.get_fieldsets(request))
            inline_admin_formset = helpers.InlineAdminFormSet(inline, formset, fieldsets)
            inline_admin_formsets.append(inline_admin_formset)
            media = media + inline_admin_formset.media

        context.update({
            'title': _('Add %s') % force_unicode(opts.verbose_name),
            'adminform': adminForm,
            'is_popup': request.REQUEST.has_key('_popup'),
            'show_delete': False,
            'media': mark_safe(media),
            'inline_admin_formsets': inline_admin_formsets,
            'errors': helpers.AdminErrorList(form, formsets),
            'root_path': self.admin_site.root_path,
            'app_label': opts.app_label,
        })
        return context

    def add_view(self, request, form_url='', extra_context=None):
        "The 'add' admin view for this model."
        context = self.get_add_view_context(request, form_url)
        context.update(extra_context or {})
        return self.render_change_form(request, context, add=True)
    add_view = transaction.commit_on_success(add_view)
