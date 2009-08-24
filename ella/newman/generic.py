from django.forms.models import BaseModelFormSet
from django.contrib.admin.options import flatten_fieldsets
from django.contrib.contenttypes.generic import generic_inlineformset_factory, \
    BaseGenericInlineFormSet as DJBaseGenericInlineFormSet
from django.forms.formsets import DELETION_FIELD_NAME
from django.forms.util import ErrorList

from ella.newman import options, utils, fields
from ella.newman.permission import get_permission, permission_filtered_model_qs, has_category_permission
from ella.newman.permission import model_category_fk_value, model_category_fk, has_object_permission
from ella.newman.permission import is_category_fk

class BaseGenericInlineFormSet(DJBaseGenericInlineFormSet):
    """
    A formset for generic inline objects to a parent.
    """
    ct_field_name = "content_type"
    ct_fk_field_name = "object_id"

    def __init__(self, data=None, files=None, instance=None, save_as_new=None, prefix=None):
        super(BaseGenericInlineFormSet, self).__init__(
            data, files, instance, save_as_new, prefix
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
        cfield = model_category_fk_value(self.model)
        if not cfield:
            return out
        # self.instance .. Article, self.model .. Placement (in GenericInlineFormSet for Placement Inline)
        view_perm = get_permission('view', self.model)
        change_perm = get_permission('change', self.model)
        perms = (view_perm, change_perm,)
        qs = permission_filtered_model_qs(out, user, perms)
        qs = utils.user_category_filter(qs, user)
        return qs

    def full_clean(self):
        super(BaseGenericInlineFormSet, self).full_clean()
        cfield = model_category_fk(self.instance)
        if not cfield:
            return
        #cat = model_category_fk_value(self.instance)

        # next part is category-based permissions (only for objects with category field)
        def add_field_error(form, field_name, message):
                err_list = ErrorList( (message,) )
                form._errors[field_name] = err_list
        user = self.form._magic_user

        # Adding new object
        for form in self.extra_forms:
            change_perm = get_permission('change', form.instance)
            if not form.has_changed():
                continue
            if cfield.name not in form.changed_data:
                continue
            add_perm = get_permission('add', form.instance)
            if not has_object_permission(user, form.instance, change_perm):
                self._non_form_errors = _('Creating objects is not permitted.')
                continue
            c = form.cleaned_data[cfield.name]
            if not has_category_permission(user, c, add_perm):
                add_field_error( form, cfield.name, _('Category not permitted') )

        # Changing existing object
        for form in self.initial_forms:
            change_perm = get_permission('change', form.instance)
            delete_perm = get_permission('delete', form.instance)
            if self.can_delete and hasattr(form, 'cleaned_data') and form.cleaned_data[DELETION_FIELD_NAME]:
                if not has_object_permission(user, form.instance, delete_perm):
                    self._non_form_errors = _('Object deletion is not permitted.')
                    continue
                if model_category_fk(form.instance) is not None and not has_category_permission(user, form.instance.category, delete_perm):
                    self._non_form_errors = _('Object deletion is not permitted.')
                    continue
            if cfield.name not in form.changed_data:
                continue
            if not has_object_permission(user, form.instance, change_perm):
                self._non_form_errors = _('Object change is not permitted.')
                continue
            c = form.cleaned_data[cfield.name]
            if not has_category_permission(user, c, change_perm):
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
        qs = permission_filtered_model_qs(f.queryset, user, perms)
        qs._newman_filtered = True #magic variable
        f._set_queryset(qs)

    def _construct_form(self, i, **kwargs):
        if hasattr(self, 'initial_form_count') and i < self.initial_form_count():
            kwargs['instance'] = self.get_queryset()[i]
        user = self.form._magic_user
        self.restrict_field_categories(self.form, user, self.model)
        return super(BaseModelFormSet, self)._construct_form(i, **kwargs)



class GenericInlineModelAdmin(options.NewmanInlineModelAdmin):
    ct_field = "content_type"
    ct_fk_field = "object_id"
    formset = BaseGenericInlineFormSet

    def __init__(self, *args, **kwargs):
        super(GenericInlineModelAdmin, self).__init__(*args, **kwargs)

    def get_formset(self, request, obj=None):
        setattr(self.form, '_magic_user', request.user) # magic variable passing to form
        setattr(self, '_magic_user', request.user) # magic variable
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
        return generic_inlineformset_factory(self.model, **defaults)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if is_category_fk(db_field):
            fld = super(GenericInlineModelAdmin, self).formfield_for_dbfield(db_field, **kwargs)#FIXME get fld.queryset different way
            kwargs.update({
                'model': self.model,
                'user': self._magic_user
            })
            return fields.CategoryChoiceField(fld.queryset, **kwargs)
        return options.formfield_for_dbfield_factory(self, db_field, **kwargs)

class GenericStackedInline(GenericInlineModelAdmin):
    template = 'newman/edit_inline/stacked.html'

class GenericTabularInline(GenericInlineModelAdmin):
    template = 'newman/edit_inline/tabular.html'

