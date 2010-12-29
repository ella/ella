from django import forms
from django.conf import settings
from django.db.models.query_utils import Q
from django.db.models import ForeignKey, SlugField, ManyToManyField, ImageField
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib import admin

SUGGEST_VIEW_LIMIT = getattr(settings, 'SUGGEST_VIEW_LIMIT', 20)
SUGGEST_VIEW_MIN_LENGTH = getattr(settings, 'SUGGEST_VIEW_MIN_LENGTH', 2)
SUGGEST_RETURN_ALL_FIELD = getattr(settings, 'SUGGEST_RETURN_ALL_FIELD', True)

class EllaModelAdmin(admin.ModelAdmin):
    registered_views = []
    actions = None

    def register(cls, test_callback, view_callback):
        cls.registered_views.append({'test': test_callback, 'view': view_callback})
    register = classmethod(register)

    def __call__(self, request, url):
        for reg in self.registered_views:
            if reg['test'](url):
                return reg['view'](self, request)

        if url and url.endswith('suggest'):
            return self.suggest_view(request)

        return super(EllaModelAdmin, self).__call__(request, url)

    def get_form(self, request, obj=None, **kwargs):
        self._magic_instance = obj # adding edited object to ModelAdmin instance.
        return super(EllaModelAdmin, self).get_form(request, obj, **kwargs)

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

    def photo_thumbnail(self, object):
        if object.photo:
            return object.photo.thumb()
        else:
            return mark_safe('<strong>%s</strong>' % ugettext('No main photo!'))
    photo_thumbnail.allow_tags = True
    photo_thumbnail.short_description = _('Photo')



class EllaAdminOptionsMixin(object):
    def formfield_for_dbfield(self, db_field, **kwargs):
        from ella.ellaadmin import widgets, fields
        custom_param_names = ('request', 'user', 'model', 'super_field', 'instance')
        custom_params = {}
        custom_params.update({
            'instance': self.__dict__.get('_magic_instance', None),
            'model': self.model
        })
        # move custom kwargs from kwargs to custom_params
        for key in kwargs:
            if key not in custom_param_names:
                continue
            custom_params[key] = kwargs[key]
            if key == 'request':
                custom_params['user'] = custom_params[key].user
        for key in custom_param_names:
            kwargs.pop(key, None)

        # TODO: Only hotfix for django 9791+
        if 'request' in kwargs:
            del kwargs['request']

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
                    'field_name': db_field.name,
                    'instance': custom_params.get('instance', None),
                    'model': custom_params.get('model'),
                })
                if 'ella.newman' in settings.INSTALLED_APPS:
                    rich_text_field = fields.RichTextAreaField(**kwargs)
                    if css_class:
                        rich_text_field.widget.attrs['class'] += ' %s' % css_class
                else:
                    # remove arguments specific to RichTextAreaField
                    specific_args = ('model', 'field_name', 'instance', 'syntax_processor_name')
                    for arg in specific_args:
                        if arg in kwargs:
                            del kwargs[arg]
                    rich_text_field = forms.CharField(**kwargs)
                    if css_class:
                        rich_text_field.widget.attrs['class'] += ' %s' % css_class
                return rich_text_field

        if db_field.name in self.raw_id_fields and isinstance(db_field, ForeignKey):
            kwargs['widget'] = widgets.ForeignKeyRawIdWidget(db_field.rel)
            return db_field.formfield(**kwargs)

        if isinstance(db_field, ImageField):
            # because we accept only (JPEG) images with RGB color profile.
            return fields.OnlyRGBImageField(db_field, **kwargs)

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
            return db_field.formfield(**kwargs)
        elif db_field.name in ('target_id', 'source_id', 'object_id',):
            kwargs['widget'] = widgets.ForeignKeyGenericRawIdWidget
            return db_field.formfield(**kwargs)

        if db_field.name == 'order':
            kwargs['widget'] = widgets.IncrementWidget
            return db_field.formfield(**kwargs)


        return super(EllaAdminOptionsMixin, self).formfield_for_dbfield(db_field, **kwargs)


class EllaAdminInline(EllaAdminOptionsMixin):

    def get_formset(self, request, obj=None):
        setattr(self.form, '_magic_user', request.user) # magic variable assigned to form
        setattr(self, '_magic_user', request.user) # magic variable
        from django.forms.models import _get_foreign_key
        setattr(self, '_magic_instance', obj)
        setattr(self, '_magic_fk', _get_foreign_key(self.parent_model, self.model, fk_name=self.fk_name))
        self.user = request.user
        return super(EllaAdminInline, self).get_formset(request, obj)

    def formfield_for_dbfield(self, db_field, **kwargs):
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
        return super(EllaAdminInline, self).formfield_for_dbfield(db_field, **kwargs)


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




