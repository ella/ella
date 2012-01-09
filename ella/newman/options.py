import logging
import re

from django import forms
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.options import InlineModelAdmin, IncorrectLookupParameters, FORMFIELD_FOR_DBFIELD_DEFAULTS
from django.contrib.admin.util import unquote
from django.contrib import messages
from django.forms.models import BaseInlineFormSet
from django import template
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.contrib.admin.views.main import ERROR_FLAG
from django.shortcuts import render_to_response
from django.db import transaction, models
from django.utils.functional import update_wrapper
from django.utils.translation import ugettext as _
from django.utils.encoding import force_unicode
from django.template.defaultfilters import striptags, truncatewords
from django.conf import settings

from ella.core.models.publishable import Publishable
from ella.newman.changelist import NewmanChangeList, FilterChangeList
from ella.newman import fields, widgets, utils
from ella.newman.models import DenormalizedCategoryUserRole, AdminUserDraft, AdminHelpItem
from ella.newman.decorators import require_AJAX
from ella.newman.permission import is_category_model, model_category_fk, model_category_fk_value, applicable_categories
from ella.newman.permission import has_category_permission, get_permission, permission_filtered_model_qs, is_category_fk
from ella.newman.forms import DraftForm
from ella.newman.xoptions import XModelAdmin
from ella.newman.licenses.models import License
from ella.newman.conf import newman_settings

log = logging.getLogger('ella.newman')

def formfield_for_dbfield_factory(cls, db_field, **kwargs):
    formfield_overrides = dict(FORMFIELD_FOR_DBFIELD_DEFAULTS, **cls.formfield_overrides)
    custom_param_names = ('request', 'user', 'model', 'super_field', 'instance')
    custom_params = {}
    # move custom kwargs from kwargs to custom_params
    for key in kwargs:
        if key not in custom_param_names:
            continue
        custom_params[key] = kwargs[key]
        if key == 'request':
            custom_params['user'] = custom_params[key].user
    for key in custom_param_names:
        kwargs.pop(key, None)

    if db_field.choices:
        return db_field.formfield(**kwargs)

    for css_class, rich_text_fields in getattr(cls, 'rich_text_fields', {}).iteritems():
        if db_field.name in rich_text_fields:
            kwargs.update({
                'required': not db_field.blank,
                'label': db_field.verbose_name,
                'field_name': db_field.name,
                'instance': custom_params.get('instance', None),
                'model': custom_params.get('model'),
            })
            rich_text_field = fields.NewmanRichTextField(**kwargs)
            if css_class:
                rich_text_field.widget.attrs['class'] += ' %s' % css_class
            return rich_text_field

    # date and datetime fields
    if isinstance(db_field, models.DateTimeField):
        kwargs.update({
            'widget': widgets.DateTimeWidget,
        })
        return db_field.formfield(**kwargs)
    elif isinstance(db_field, models.DateField):
        kwargs.update({
            'widget': widgets.DateWidget,
        })
        return db_field.formfield(**kwargs)

    if isinstance(db_field, models.ImageField):
        # we accept only (JPEG) images with RGB color profile.
        kwargs.update({
            'label': db_field.verbose_name,
        })
        return fields.RGBImageField(db_field, **kwargs)

    if db_field.name in cls.raw_id_fields and isinstance(db_field, models.ForeignKey):
        kwargs.update({
            'label': db_field.verbose_name,
            'widget': widgets.ForeignKeyRawIdWidget(db_field.rel),
            'required': not db_field.blank,
        })
        return fields.RawIdField(db_field.rel.to.objects.all(), **kwargs)

    if db_field.name in getattr(cls, 'suggest_fields', {}).keys() \
                        and isinstance(db_field, (models.ForeignKey, models.ManyToManyField)):
        kwargs.update({
            'required': not db_field.blank,
            'label': db_field.verbose_name,
            'model': cls.model,
            'lookup': cls.suggest_fields[db_field.name]
        })
        return fields.AdminSuggestField(db_field, **kwargs)

    if isinstance(db_field, models.ForeignKey) and issubclass(db_field.rel.to, ContentType):
        kwargs['widget'] = widgets.ContentTypeWidget
        return db_field.formfield(**kwargs)
    elif db_field.name in ('target_id', 'source_id', 'object_id', 'related_id', 'obj_id'):
        kwargs['widget'] = widgets.ForeignKeyGenericRawIdWidget
        return db_field.formfield(**kwargs)

    if db_field.name == 'order':
        kwargs['widget'] = widgets.OrderFieldWidget
        return db_field.formfield(**kwargs)

    # magic around restricting category choices in all ForeignKey (related to Category) fields
    if is_category_fk(db_field) and 'model' in custom_params:
        kwargs.update({
            'model': custom_params['model'],
            'user': custom_params['user']
        })
        super_qs = custom_params['super_field'].queryset
        return fields.CategoryChoiceField(super_qs, **kwargs)

    if db_field.__class__ in formfield_overrides:
        kwargs = dict(formfield_overrides[db_field.__class__], **kwargs)
        return db_field.formfield(**kwargs)

    return db_field.formfield(**kwargs)

from django.contrib.admin.helpers import InlineAdminForm, InlineAdminFormSet
class InlineNewmanFormset(InlineAdminFormSet):
    
    def __iter__(self):
        for form, original in zip(self.formset.initial_forms, self.formset.get_queryset()):
            yield InlineAdminForm(self.formset, form, self.fieldsets,
                self.opts.prepopulated_fields, original, self.readonly_fields,
                model_admin=self.opts)
        for form in self.formset.extra_forms:
            yield InlineAdminForm(self.formset, form, self.fieldsets,
                self.opts.prepopulated_fields, None, self.readonly_fields,
                model_admin=self.opts)

class NewmanModelAdmin(XModelAdmin):
    changelist_view_cl = NewmanChangeList
    actions = None

    def get_template_list(self, base_template):
        model = self.model
        opts = model._meta
        app_label = opts.app_label

        return [
            "newman/%s/%s/%s" % (app_label, opts.object_name.lower(), base_template),
            "newman/%s/%s" % (app_label, base_template),
            "newman/%s" % base_template
        ]

    def __init__(self, *args, **kwargs):
        super(NewmanModelAdmin, self).__init__(*args, **kwargs)

        # newman's custom templates
        self.delete_confirmation_template = self.get_template_list('delete_confirmation.html')
        self.delete_selected_confirmation_template = self.get_template_list('delete_selected_confirmation.html')
        self.object_history_template = self.get_template_list('object_history.html')
        self.change_form_template = self.get_template_list('change_form.html')
        self.change_list_template = self.get_template_list('change_list.html')
        self.filters_template = self.get_template_list('filters.html')

        self.list_per_page = newman_settings.DEFAULT_LIST_PER_PAGE
        self.model_content_type = ContentType.objects.get_for_model(self.model)
        self.saveasnew_add_view = self.add_json_view
        # useful when self.queryset(request) is called multiple times
        self._cached_queryset_request_id = -1
        self._cached_queryset = None

    def _media(self):

        js = []
        if self.actions is not None:
            js.extend(['js/actions.min.js'])
        if self.prepopulated_fields:
            js.append('js/urlify.js')
            js.append('js/prepopulate.min.js')
        if self.opts.get_ordered_objects():
            js.extend(['js/getElementsBySelector.js', 'js/dom-drag.js' , 'js/admin/ordering.js'])

        return forms.Media(js=['%s%s' % (settings.ADMIN_MEDIA_PREFIX, url) for url in js])

    media = property(_media)

    def get_form(self, request, obj=None, **kwargs):
        self._magic_instance = obj # adding edited object to ModelAdmin instance.
        return super(NewmanModelAdmin, self).get_form(request, obj, **kwargs)

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.module_name

        urlpatterns = patterns('',
            url(r'^suggest/$',
                wrap(self.suggest_view),
                name='%s_%s_suggest' % info),
            url(r'^filters/$',
                wrap(self.filters_view),
                name='%s_%s_filters' % info),
            url(r'^log/$',
                wrap(self.log_view),
                name='%s_%s_log' % info),
            url(r'^(.+)/help/$',
                wrap(self.model_help_view),
                name='%s_%s_help' % info),
            url(r'^(.+)/draft/save/$',
                wrap(self.save_draft_view),
                name='%s_%s_save_draft' % info),
            url(r'^(.+)/draft/load/$',
                wrap(self.load_draft_view),
                name='%s_%s_load_draft' % info),
            url(r'^(.+)/draft/delete/$',
                wrap(self.delete_draft_view),
                name='%s_%s_delete_draft' % info),
            url(r'^add/json/$',
                wrap(self.add_json_view),
                name='%s_%s_add_json' % info),
            url(r'^(.+)/json/$',
                wrap(self.change_json_view),
                name='%s_%s_change_json' % info),
            url(r'^(.+)/json/detail/$',
                wrap(self.model_detail_json_view),
                name='%s_%s_json_detail' % info),
        )
        urlpatterns += super(NewmanModelAdmin, self).get_urls()
        return urlpatterns

    @require_AJAX
    def model_help_view(self, request, extra_context=None):
        """ Returns help for model and his fields. """

        base_help_items = AdminHelpItem.objects.filter(ct=self.model_content_type, lang=settings.LANGUAGE_CODE).values()
        model_help = base_help_items.filter(field='')
        if model_help:
            model_help = model_help[0]

        model_fields = self.model._meta.fields

        bhi = {}
        help_total = []

        for f in model_fields:
            if f.editable:
                bhi[f.name] = {'verbose_name': f.verbose_name, 'help_text': f.help_text}

        for h in base_help_items:
            try:
                bhi[h['field']].update(h)
            except KeyError:
                pass
                #log.warning('Field %s is not in model %s' % (h['field'], self.model))

        for f in model_fields:
            if f.editable:
                help_total.append(bhi[f.name])

        context = {
            'ct': self.model_content_type,
            'model_help': model_help,
            'model_doc': self.model.__doc__,
            'fields_help': help_total,
            'inline_help_items': None
        }

        return render_to_response(
            self.get_template_list('model_help.html'),
            context,
            context_instance=template.RequestContext(request)
        )

    @require_AJAX
    def save_draft_view(self, request, extra_context=None):
        """ Autosave data (dataloss-prevention) or save as (named) template """
        def delete_too_old_drafts():
            " remove autosaves too old to rock'n'roll "
            to_delete = AdminUserDraft.objects.filter(title__exact='', user=request.user).order_by('-ts')
            for draft in to_delete[newman_settings.AUTOSAVE_MAX_AMOUNT:]:
                log.debug('Deleting too old user draft (autosave) %d' % draft.pk)
                draft.delete()

        self.register_newman_variables(request)
        data = request.POST.get('data', None)
        if not data:
            return utils.JsonResponseError(_('No data passed in POST variable "data".'), status=newman_settings.STATUS_VAR_MISSING)
        title = request.POST.get('title', '')
        id = request.POST.get('id', None)

        if id:
            # modifying existing draft/preset
            try:
                obj = AdminUserDraft.objects.get(pk=id)
                obj.data = data
                obj.title = title
                obj.save()
            except AdminUserDraft.DoesNotExist:
                obj = AdminUserDraft.objects.create(
                    ct=self.model_content_type,
                    user=request.user,
                    data=data,
                    title=title
                )
        else:
            obj = AdminUserDraft.objects.create(
                ct=self.model_content_type,
                user=request.user,
                data=data,
                title=title
            )
            delete_too_old_drafts()
        data = {'id': obj.pk, 'title': obj.__unicode__()}
        return utils.JsonResponse(_('Preset %s was saved.' % obj.__unicode__()), data)

    @require_AJAX
    def load_draft_view(self, request, extra_context=None):
        """ Returns draft identified by request.GET['id'] variable. """
        self.register_newman_variables(request)
        id = request.GET.get('id', None)
        if not id:
            return utils.JsonResponse(_('No id found in GET variable "id".'), status=newman_settings.STATUS_VAR_MISSING)
        drafts = AdminUserDraft.objects.filter(
            ct=self.model_content_type,
            user=request.user,
            pk=id
        )
        if not drafts:
            return utils.JsonResponse(_('No matching draft found.'), status=newman_settings.STATUS_OBJECT_NOT_FOUND)
        draft = drafts[0]
        return utils.JsonResponse(_('Loaded draft "%s"' % draft.__unicode__()), draft.data)

    @require_AJAX
    def delete_draft_view(self, request, extra_context=None):
        self.register_newman_variables(request)
        id = request.GET.get('id', None)
        if not id:
            return utils.JsonResponse(_('No id found in GET variable "id".'), status=newman_settings.STATUS_VAR_MISSING)
        try:
            draft = AdminUserDraft.objects.get(
                ct=self.model_content_type,
                user=request.user,
                pk=id
            )
        except AdminUserDraft.DoesNotExist:
            return utils.JsonResponse(_('No matching draft found.'), status=newman_settings.STATUS_OBJECT_NOT_FOUND)
        msg = _('Draft %s was deleted.' % draft.__unicode__())
        draft.delete()
        return utils.JsonResponse(msg)

    @require_AJAX
    def filters_view(self, request, extra_context=None):
        "stolen from: The 'change list' admin view for this model."
        self.register_newman_variables(request)
        opts = self.model._meta
        app_label = opts.app_label
        try:
            cl = FilterChangeList(request, self.model, self.list_display, self.list_display_links, self.list_filter,
                self.date_hierarchy, self.search_fields, self.list_select_related, self.list_per_page, self.list_editable, self)
        except IncorrectLookupParameters:
            # Wacky lookup parameters were given, so redirect to the main
            # changelist page, without parameters, and pass an 'invalid=1'
            # parameter via the query string. If wacky parameters were given and
            # the 'invalid=1' parameter was already in the query string, something
            # is screwed up with the database, so display an error page.
            if ERROR_FLAG in request.GET.keys():
                return render_to_response('newman/invalid_setup.html', {'title': _('Database error')})
            #return HttpResponseRedirect(request.path + '?' + ERROR_FLAG + '=1')
            return utils.JsonResponseRedirect(request.path + '?' + ERROR_FLAG + '=1')
        cl.formset = None

        context = {
            'title': cl.title,
            'is_popup': cl.is_popup,
            'cl': cl,
            'has_add_permission': self.has_add_permission(request),
            'root_path': self.admin_site.root_path,
            'app_label': app_label,
        }
        context.update(extra_context or {})
        out= render_to_response(self.filters_template or 'newman/filters.html',
            context,
            context_instance=template.RequestContext(request)
        )
        return HttpResponse(out, mimetype='text/plain;charset=utf-8')

    @require_AJAX
    def log_view(self, request, extra_context=None):
        self.register_newman_variables(request)

        ct = ContentType.objects.get_for_model(self.model)
        if ct.model_class() == Publishable:
            publishable_cts = []
            cts = ContentType.objects.all()
            for ctc in cts:
                if ctc.model_class() and issubclass(ctc.model_class(), Publishable):
                    publishable_cts.append(ctc.id)
            params= {'content_type__in': publishable_cts}
        else:
            params = {'content_type': ct}

        if not request.user.is_superuser:
            params.update({'user': request.user})

        entries = utils.get_log_entries(limit=15, filters=params)
        context = {'entry_list': entries, 'ct': ct}

        return render_to_response(self.get_template_list('action_log.html'), context, context_instance=template.RequestContext(request))


    #@require_AJAX
    def changelist_view(self, request, extra_context=None):
        self.register_newman_variables(request)

        # save per user filtered content type.
        is_popup = False
        req_path = request.get_full_path()
        ct = ContentType.objects.get_for_model(self.model)
        # persistent filter for non-popupped changelists only
        key = 'filter__%s__%s' % (ct.app_label, ct.model)
        if req_path.find('pop') >= 0: # if popup is displayed, remove pop string from request path
            is_popup = True
            req_path = re.sub(r'(.*)(pop=&|&pop=|pop=|pop&|&pop|pop)(.*)', r'\1\3', req_path)
        if req_path.endswith('?') and is_popup:
            req_path = '' # if popup with no active filters is displayed, do not save empty filter settings
        if req_path.find('?') > 0:
            url_args = req_path.split('?', 1)[1]
            utils.set_user_config_db(request.user, key, url_args)
            log.debug('SAVING FILTERS %s' % url_args)
        else:
            user_filter = utils.get_user_config(request.user, key)
            if user_filter:
                if is_popup:
                    user_filter = 'pop&%s' % user_filter
                redirect_to = '%s?%s' % (request.path, user_filter)
                if not redirect_to.endswith('?q='):
                    log.debug('REDIRECTING TO %s' % redirect_to)
                    return utils.JsonResponseRedirect(redirect_to)

        context = super(NewmanModelAdmin, self).get_changelist_context(request)
        if type(context) != dict:
            return context

        if context['media']:
            raw_media = self.prepare_media(context['media'])
            context['media'] = raw_media

        context['is_filtered'] = context['cl'].is_filtered()
        context['is_user_category_filtered'] = utils.is_user_category_filtered( self.queryset(request) )
        context.update(extra_context or {})
        return render_to_response(self.change_list_template, context, context_instance=template.RequestContext(request))

    @require_AJAX
    def suggest_view(self, request, extra_context=None):
        self.register_newman_variables(request)

        if not ('f' in request.GET.keys() and 'q' in request.GET.keys()):
            raise AttributeError, 'Invalid query attributes. Example: ".../?f=field_a&f=field_b&q=search_term&o=offset"'
        elif len(request.GET.get('q')) < newman_settings.SUGGEST_VIEW_MIN_LENGTH:
            return HttpResponse( '', mimetype='text/plain;charset=utf-8' )

        offset = 0
        if 'o' in request.GET.keys() and request.GET.get('o'):
            offset = int(request.GET.get('o'))
        limit = offset + newman_settings.SUGGEST_VIEW_LIMIT

        model_fields = [mf.name for mf in self.model._meta.fields]
        lookup_fields = []
        lookup_value = request.GET.get('q')
        lookup = None
        has_non_lookup_attr = False
        all_fields = [u'id'] + request.GET.getlist('f')

        for lf in all_fields:
            if lf in model_fields or lf.split('__')[0] in model_fields:
                lookup_fields.append(lf)
            elif hasattr(self.model, lf):
                has_non_lookup_attr = True
            else:
                raise AttributeError, 'Model "%s" has not field "%s". Possible fields are "%s".' \
                                    % (self.model._meta.object_name, lf, ', '.join(model_fields))

        for f in lookup_fields:
            lookup_key = str('%s__icontains' % f)
            if not lookup:
                lookup = models.Q(**{lookup_key: lookup_value})
            else:
                lookup = lookup | models.Q(**{lookup_key: lookup_value})
        # user role based category filtering
        if not is_category_model(self.model):
            category_field = model_category_fk(self.model)
            if category_field and request.user:
                applicable = applicable_categories(request.user)
                args_lookup = { '%s__in' % category_field.name: applicable}
                lookup = lookup & models.Q(**args_lookup)
        else:
            applicable = applicable_categories(request.user)
            lookup = lookup & models.Q(pk__in=applicable)
        # user category filter
        qs = utils.user_category_filter(self.model.objects.filter(lookup), request.user)

        if not has_non_lookup_attr:
            data = qs.values(*lookup_fields)
        else:
            data = qs.only(*lookup_fields)

        def construct_row(inst, fields):
            row = {}
            for f in fields:
                attr = getattr(inst, f)
                if callable(attr):
                    row[f] = attr()
                else:
                    row[f] = attr
                row[f] = truncatewords(striptags(unicode(row[f])), 5)
            return row

        if has_non_lookup_attr:
            outdata = []
            for i in data:
                outdata.append(construct_row(i, all_fields))
            data = outdata

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
        cnt = len(data)
        data = list(data)
        if offset >= len(data): return HttpResponse('SPECIAL: OFFSET OUT OF RANGE', mimetype='text/plain')
        data.sort(cmp=compare, key=lambda x: x[lookup_fields[1]])
        data = data[offset:limit]

        ft = []
        ft.append('{cnt:%d}' % cnt)
        for item in data:
            ft.append( "%s".encode('utf-8') % '|'.join("%s" % item[f] for f in all_fields) )

        return HttpResponse( '\n'.join(ft), mimetype='text/plain;charset=utf-8' )

    def register_newman_variables(self, request):
        self.user = request.user

    def has_view_permission(self, request, obj):
        opts = self.opts
        view_perm = '%s.view_%s' % ( opts.app_label, opts.object_name.lower() )
        return request.user.has_perm(view_perm)

    def has_model_view_permission(self, request, obj=None):
        """ returns True if user has permission to view this model, otherwise False. """
        # try to find view or change perm. for given user in his permissions or groups permissions
        can_change = super(NewmanModelAdmin, self).has_change_permission(request, obj)
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
        cfield = model_category_fk_value(obj)
        if obj is None or not cfield:
            if request.method == 'POST':
                return super(NewmanModelAdmin, self).has_change_permission(request, obj)
            else:
                return self.has_model_view_permission(request, obj)

        opts = self.opts
        change_perm = '%s.%s' % ( opts.app_label, opts.get_change_permission() )
        view_perm = '%s.view_%s' % ( opts.app_label, opts.object_name.lower() )
        can_view = has_category_permission( request.user, cfield, view_perm )
        can_change = has_category_permission( request.user, cfield, change_perm )

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
        roles = DenormalizedCategoryUserRole.objects.filter(
            user_id=user.pk,
            permission_codename=del_perm
        )
        if roles:
            return True
        # no permission found
        return False

    def has_add_permission(self, request):
        "Returns True if the given request has permission to add an object."
        opts = self.opts
        add_perm = opts.app_label + '.' + opts.get_add_permission()
        if request.user.has_perm(add_perm):
            return True
        user = request.user
        roles = DenormalizedCategoryUserRole.objects.filter(
            user_id=user.pk,
            permission_codename=add_perm
        )
        if roles:
            return True
        # no permission found
        return False


    def get_change_view_inline_formsets(self, request, obj, formsets, media):
        inline_admin_formsets = []
        self._raw_inlines = {}
        for inline, formset in zip(self.inline_instances, formsets):
            self._raw_inlines[str(inline.model._meta).replace('.', '__')] = formset
            fieldsets = list(inline.get_fieldsets(request, obj))
            inline_admin_formset = InlineNewmanFormset(inline, formset, fieldsets)
            inline_admin_formsets.append(inline_admin_formset)
            media = media + inline_admin_formset.media
        return inline_admin_formsets, media

    def json_error_response(self, request, context):
        """
        Chyby v polich formulare
        Chyba v poli formulare napr.: context['adminform'].form['slug'].errors
        Chyba v poli inline napr.: context['inline_admin_formsets'][0].formset.errors
                   tj.: [{'content': [u'Toto pole je povinn\xe9.']}]

                id inline v sablone: id_ + context['inline_admin_formsets'][0].formset.prefix + [poradove cislo formsetu tj. 0 + jmeno sloupce
                priklad id: id_articlecontents_set-0-content
        """
        fcounter = {}
        def get_formset_counter(fset):
            if fset not in fcounter:
                fcounter[fset] = 0
            else:
                fcounter[fset] += 1
            return fcounter[fset]

        def give_me_unicode(ei):
            if not hasattr(ei, '__unicode__'):
                return u'%s' % ei
            return ei.__unicode__()

        error_list = []
        # Form fields
        frm = context['adminform'].form
        for field_name in frm.fields:
            field = frm[field_name]
            if field.errors:
                err_dict = {
                    'id': u"id_%s" % field_name,
                    'label': u"%s" % field.label,
                    'messages': map(lambda item: u'%s' % item, map(give_me_unicode, field.errors))
                }
                error_list.append(err_dict)
        # Inline Form fields
        for fset in context['inline_admin_formsets']:
            for err_item in fset.formset.errors:
                counter = get_formset_counter(fset.formset.prefix)
                for key in err_item:
                    label = u''
                    """
                    for mfield in fset.formset.model._meta.fields:
                        if mfield.name == key:
                            label = mfield.verbose_name
                            break
                    """
                    for fkey, mfield in fset.formset.form.base_fields.items():
                        if fkey == key:
                            if hasattr(mfield.label, '__unicode__'):
                                label = mfield.label.__unicode__()
                            else:
                                label = mfield.label.__str__()
                            break

                    err_dict = {
                        'id': u'id_%s-%d-%s' % (fset.formset.prefix, counter, key),
                        'label': u"%s" % label,
                        'messages': map(lambda item: item, map(give_me_unicode, err_item[key]))
                    }
                    error_list.append(err_dict)
        # Other errors (e.g. db errors)
        if 'error_dict' in context and 'id___all__' in context['error_dict']:
            error_list.append({'messages': context['error_dict']['id___all__'], 'id': 'id___all__',})

        return utils.JsonResponse(_('Please correct errors in form'), errors=error_list, status=newman_settings.STATUS_FORM_ERROR)

    def change_view_process_context(self, request, context, object_id):
        form  = context['raw_form']

        # raw forms for JS manipulations
        raw_frm_all = {
            'form': form,
            'inlines': self._raw_inlines
        }

        # form for autosaved and draft objects
        draft_form = DraftForm(user=request.user, content_type=self.model_content_type)

        info = self.admin_site.app_name, self.model._meta.app_label, self.model._meta.module_name
        rev = '%s:%s_%s_change_json' % info
        context.update({
            'media': self.prepare_media(context['media']),
            'raw_form': raw_frm_all,
            'draft_form': draft_form,
            'save_url': reverse(rev, args=[object_id])
        })
        return context

    def change_view_prepare_context(self, request, object_id):
        self.register_newman_variables(request)
        out = self.change_view_preprocess(request, object_id)
        if out is not None:
            # HttpReponse
            return out
        context = self.get_change_view_context(request, object_id)
        # Newman's additions to the context
        self.change_view_process_context(request, context, object_id)
        return context

    def model_detail_json_view(self, request, object_id, extra_context=None):
        " Outputs basic object's data. "
        obj = None
        try:
            obj = self.queryset(request).get(pk=unquote(object_id))
        except obj.DoesNotExist:
            obj = None
        if not self.has_model_view_permission(request, obj):
            raise PermissionDenied

        result_dict = dict()
        for field in obj._meta.fields:
            result_dict[field.name] = field.value_to_string(obj)

        return utils.JsonResponse(
            'JSON object detail data.',
            result_dict,
            status=newman_settings.STATUS_OK
        )

    @transaction.commit_on_success
    def change_json_view(self, request, object_id, extra_context=None):
        "The 'change' admin view for this model."
        if request.method.upper() != 'POST':
            msg = _('This view is designed for saving data only, thus POST method is required.')
            return HttpResponseForbidden(msg)

        context = self.change_view_prepare_context(request, object_id)
        if type(context) != dict:
            obj = self.get_change_view_object(object_id)
            opts = obj._meta

            if request.FILES and not request.is_ajax():
                return_url = '%s#/%s/%s/' % (reverse('newman:index'), opts.app_label, opts.module_name)
                if request.POST.get('_continue'):
                    return_url += '%s/' % object_id
                if request.POST.get('_addanother'):
                    return_url += 'add/'
                return HttpResponseRedirect(return_url)

            redir = request.POST.get('http_redirect_to', None)
            if redir:
                return utils.JsonResponseRedirect(redir)

            return utils.JsonResponse(
                _('The %(name)s "%(obj)s" was changed successfully.') % {'name': force_unicode(opts.verbose_name), 'obj': force_unicode(obj)},
                {'id': obj.pk, 'title': obj.__unicode__(),},
                status=newman_settings.STATUS_OK
            )
        context.update(extra_context or {})
        return self.json_error_response(request, context)  # Json response

    def change_view(self, request, object_id, extra_context=None):
        "The 'change' admin view for this model."
        if request.method.upper() != 'GET':
            msg = _('This view is designed for viewing form, thus GET method is required.')
            return HttpResponseForbidden(msg)
        context = self.change_view_prepare_context(request, object_id)
        context.update(extra_context or {})
        obj = self.get_change_view_object(object_id)
        return self.render_change_form(request, context, change=True, obj=obj)

    def get_add_view_context(self, request, form_url):
        self.register_newman_variables(request)
        context = super(NewmanModelAdmin, self).get_add_view_context(request, form_url)

        # form for autosaved and draft objects
        draft_form = DraftForm(user=request.user, content_type=self.model_content_type)

        info = self.admin_site.app_name, self.model._meta.app_label, self.model._meta.module_name
        rev = '%s:%s_%s_add_json' % info
        context.update({
            'media': self.prepare_media(context['media']),
            'draft_form': draft_form,
            'save_url': reverse(rev)
        })
        return context

    def get_inline_admin_formset(self, inline, formset, fieldsets):
        return InlineNewmanFormset(inline, formset, fieldsets)

    @require_AJAX
    def delete_view(self, request, object_id, extra_context=None):
        try:
            result = super(NewmanModelAdmin, self).delete_view(request, object_id, extra_context)
            if not isinstance(result, HttpResponseRedirect):
                return result
        except Exception, e:
            # in case of exception return JSON error dict instead of 500.html
            return utils.JsonResponseError(str(e))
        # create JsonResponse containing success message
        return utils.JsonResponse(_('Object was deleted.'))
        #return utils.JsonResponseRedirect(result['Location'])

    @transaction.commit_on_success
    def add_json_view(self, request, form_url='', extra_context=None):
        "The 'add' admin view for this model. Communicating with client in JSON format only."
        if request.method.upper() != 'POST':
            msg = _('This view is designed for saving data only, thus POST method is required.')
            return HttpResponseForbidden(msg)
        context = self.get_add_view_context(request, form_url)
        context.update(extra_context or {})
        if 'object_added' in context:
            obj = context['object']
            msg = unicode(list(messages.get_messages(request))[0])

            if request.FILES and not request.is_ajax():
                return_url = '%s#/%s/%s/' % (reverse('newman:index'), obj._meta.app_label, obj._meta.module_name)
                if request.POST.get('_continue'):
                    return_url += '%s/' % obj.pk
                if request.POST.get('_addanother'):
                    return_url += 'add/'
                return HttpResponseRedirect(return_url)

            return utils.JsonResponse(msg, {
                    'id': obj.pk,
                    'title': getattr(obj, '__unicode__', obj.__str__)(),
                })

        elif 'error_dict' in context:
            return self.json_error_response(request, context)

    def add_view(self, request, form_url='', extra_context=None):
        "The 'add' admin view for this model."
        if request.method.upper() != 'GET':
            msg = _('This view is designed for viewing form, thus GET method is required.')
            return HttpResponseForbidden(msg)
        context = self.get_add_view_context(request, form_url)
        context.update(extra_context or {})
        return self.render_change_form(request, context, add=True)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if is_category_fk(db_field):
            kwargs['super_field'] = super(NewmanModelAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        kwargs.update({
            'model': self.model,
            'user': self.user,
            'instance': self.__dict__.get('_magic_instance', None),
        })
        return formfield_for_dbfield_factory(self, db_field, **kwargs)

    def queryset(self, request):
        """
        First semi-working draft of category-based permissions. It will allow permissions to be set per category
        effectively hiding the content the user has no permission to see/change.
        """
        # return cached queryset, if possible
        if self._cached_queryset_request_id == id(request) and type(self._cached_queryset) != type(None):
            return self._cached_queryset

        q = super(NewmanModelAdmin, self).queryset(request)
        # user category filter
        qs = utils.user_category_filter(q, request.user)

        # if self.model is licensed filter queryset
        if License._meta.installed:
            exclude_pks = License.objects.unapplicable_for_model(self.model)
            qs_tmp = qs.exclude(pk__in=exclude_pks)
            utils.copy_queryset_flags(qs_tmp, qs)
            qs = qs_tmp

        if request.user.is_superuser:
            return qs
        view_perm = self.opts.app_label + '.' + 'view_' + self.model._meta.module_name.lower()
        change_perm = self.opts.app_label + '.' + 'change_' + self.model._meta.module_name.lower()
        perms = (view_perm, change_perm,)
#        return permission_filtered_model_qs(qs, request.user, perms)
        qs_tmp = permission_filtered_model_qs(qs, request.user, perms)
        utils.copy_queryset_flags(qs_tmp, qs)

        # cache the result
        self._cached_queryset_request_id = id(request)
        self._cached_queryset = qs_tmp
        return qs_tmp


    def prepare_media(self, standard_media):
        """ Returns raw media paths for ajax loading """

        raw_media = []
        if standard_media._css.has_key('screen'):
            raw_media.extend(standard_media._css['screen'])
        raw_media.extend(standard_media._js)
        return raw_media

class NewmanInlineFormSet(BaseInlineFormSet):
    def get_queryset(self):
        user = self.form._magic_user
        if not hasattr(self, '_queryset'):
            if self.queryset is not None:
                qs = self.queryset
            else:
                qs = self.model._default_manager.get_query_set()
            # category based permissions
            if not user.is_superuser:
                category_fk = model_category_fk(self.model)
                if category_fk:
                    # in ListingInlineOptions: self.instance .. Placement instance, self.model .. Listing
                    view_perm = get_permission('view', self.model)
                    change_perm = get_permission('change', self.model)
                    perms = (view_perm, change_perm,)
                    qs = permission_filtered_model_qs(qs, user, perms)
            # user filtered categories
            qs = utils.user_category_filter(qs, user)

            if self.max_num > 0:
                self._queryset = qs[:self.max_num]
            else:
                self._queryset = qs
        return self._queryset

class NewmanInlineModelAdmin(InlineModelAdmin):
    formset = NewmanInlineFormSet

    def _media(self):
        js = []
        if self.prepopulated_fields:
            js.append('js/urlify.js')
            js.append('js/prepopulate.min.js')
        if self.filter_vertical or self.filter_horizontal:
            js.extend(['js/SelectBox.js' , 'js/SelectFilter2.js'])
        return forms.Media(js=['%s%s' % (settings.ADMIN_MEDIA_PREFIX, url) for url in js])
    media = property(_media)

    def get_formset(self, request, obj=None):
        setattr(self.form, '_magic_user', request.user) # magic variable assigned to form
        setattr(self, '_magic_user', request.user) # magic variable
        from django.forms.models import _get_foreign_key
        setattr(self, '_magic_instance', obj)
        setattr(self, '_magic_fk', _get_foreign_key(self.parent_model, self.model, fk_name=self.fk_name))
        self.user = request.user
        return super(NewmanInlineModelAdmin, self).get_formset(request, obj)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if is_category_fk(db_field):
            kwargs['super_field'] = super(NewmanInlineModelAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        inst = None
        # Inlined object is requested by RichTextField (the field needs to lookup SrcText)
        if hasattr(self, '_magic_instance') and self._magic_instance:
            instances = self.model.objects.filter(**{self._magic_fk.name: self._magic_instance.pk})
            inst = None
            if instances:
                inst = list(instances)
        kwargs.update({
            'model': self.model,
            'user': self._magic_user,
            'instance': inst,
        })
        return formfield_for_dbfield_factory(self, db_field, **kwargs)

class NewmanStackedInline(NewmanInlineModelAdmin):
    template = 'newman/edit_inline/stacked.html'

class NewmanTabularInline(NewmanInlineModelAdmin):
    template = 'newman/edit_inline/tabular.html'

class NewmanPrettyInline(NewmanInlineModelAdmin):
    template = 'newman/edit_inline/pretty.html'
