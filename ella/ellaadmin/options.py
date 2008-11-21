from django import forms
from django.conf import settings
from django.db.models.query_utils import Q
from django.db.models import ForeignKey, SlugField, ManyToManyField
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin

from ella.ellaadmin import widgets, fields

SUGGEST_VIEW_LIMIT = getattr(settings, 'SUGGEST_VIEW_LIMIT', 15)
SUGGEST_VIEW_MIN_LENGTH = getattr(settings, 'SUGGEST_VIEW_MIN_LENGTH', 2)
SUGGEST_RETURN_ALL_FIELD = getattr(settings, 'SUGGEST_RETURN_ALL_FIELD', True)

class EllaModelAdmin(admin.ModelAdmin):

    def __call__(self, request, url):
        if url and url.endswith('suggest'):
            return self.suggest_view(request)

        return super(EllaModelAdmin, self).__call__(request, url)

    def suggest_view(self, request, extra_context=None):

        # accepts only ajax calls if not DEBUG
        if not request.is_ajax() and not settings.DEBUG:
            raise Http404

        if not ('f' in request.GET.keys() and 'q' in request.GET.keys()):
            raise AttributeError, 'Invalid query attributes. Example: ".../?f=field_a&f=field_b&q=search_term"'
        elif len(request.GET.get('q')) < SUGGEST_VIEW_MIN_LENGTH:
            return HttpResponse('', mimetype='text/plain;charset=utf-8')

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
            data = self.model.objects.filter(lookup).values(*lookup_fields)[:SUGGEST_VIEW_LIMIT]
        else:
            data = self.model.objects.filter(lookup).values(*lookup_fields[:2])[:SUGGEST_VIEW_LIMIT]

        ft = []
        for item in data:
            if SUGGEST_RETURN_ALL_FIELD:
                ft.append("%s".encode('utf-8') % '|'.join("%s" % item[f] for f in lookup_fields))
            else:
                ft.append("%s".encode('utf-8') % '|'.join("%s" % item[f] for f in lookup_fields[:2]))

        return HttpResponse('\n'.join(ft), mimetype='text/plain;charset=utf-8')


class EllaAdminOptionsMixin(object):
    def formfield_for_dbfield(self, db_field, **kwargs):
        if isinstance(db_field, SlugField):
            kwargs.update({
                'required': not db_field.blank,
                'max_length': db_field.max_length,
                'label': db_field.verbose_name,
                'error_message': _('Enter a valid slug.'),
})
            return forms.RegexField('^[0-9a-z-]+$', **kwargs)

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

        if db_field.name in self.raw_id_fields and isinstance(db_field, ForeignKey):
            kwargs['widget'] = widgets.ForeignKeyRawIdWidget(db_field.rel)
            return db_field.formfield(**kwargs)

        if db_field.name in getattr(self, 'suggest_fields', {}).keys() and isinstance(db_field, (ForeignKey, ManyToManyField)):
            kwargs.update({
                'required': not db_field.blank,
                'label': db_field.verbose_name,
})
            if isinstance(db_field, ForeignKey):
                return fields.GenericSuggestField([db_field, self.model, self.suggest_fields[db_field.name]], **kwargs)
            return fields.GenericSuggestFieldMultiple([db_field, self.model, self.suggest_fields[db_field.name]], **kwargs)

        if db_field.name in ('target_ct', 'source_ct', 'content_type',):
            kwargs['widget'] = widgets.ContentTypeWidget
        elif db_field.name in ('target_id', 'source_id', 'object_id',):
            kwargs['widget'] = widgets.ForeignKeyGenericRawIdWidget

        return super(EllaAdminOptionsMixin, self).formfield_for_dbfield(db_field, **kwargs)


class RefererAdminMixin(object):
    """ Enables redirect back to site from model detail in admin. """
    def __call__(self, request, url):
        if 'memorize_referer' in request.GET and 'HTTP_REFERER' in request.META:
            if 'admin_redirect_after_change' not in request.session:
                request.session['admin_redirect_after_change'] = request.META['HTTP_REFERER']
        return super(RefererAdminMixin, self).__call__(request, url)

    def save_change(self, request, model, form):
        """ custom redirection back to thread page on portal """
        out = super(RefererAdminMixin, self).save_change(request, model, form)
        if isinstance(out, HttpResponseRedirect) and 'admin_redirect_after_change' in request.session:
            out = HttpResponseRedirect(request.session['admin_redirect_after_change'])
            del request.session['admin_redirect_after_change']
        return out


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




