import Image
import logging

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from django.forms import fields
from django.forms.util import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.forms.models import ModelChoiceField
from django.db.models.fields.related import ManyToManyField

from ella.newman import widgets, utils
from ella.newman.permission import get_permission, permission_filtered_model_qs, has_category_permission

log = logging.getLogger('ella.newman')

class AdminSuggestField(fields.Field):
    """
    Admin field with AJAX suggested values.
    Only ForeignKey or ManyToMany fields is possible.
    """

    default_error_messages = {
        'required': _(u'This field is required.'),
        'invalid_choice': _(u'Select a valid choice. %(value)s is not one of the available choices.'),
        'invalid_list': _(u'Enter a list of values.'),
    }

    def __init__(self, db_field, **kwargs):
        self.widget = widgets.AdminSuggestWidget(db_field, **kwargs)
        self.db_field = db_field
        del (kwargs['model'], kwargs['lookup'])
        self.is_m2m = isinstance(db_field, ManyToManyField)

        super(AdminSuggestField, self).__init__(**kwargs)

    def clean(self, value):
        if self.required and value in fields.EMPTY_VALUES:
            raise ValidationError(self.error_messages['required'])
        elif value in fields.EMPTY_VALUES:
            if self.is_m2m:
                return []
            return None

        if self.is_m2m:
            value = [int(v) for v in value.split(',')]
            if not isinstance(value, (list, tuple)):
                raise ValidationError(self.error_messages['invalid_list'])

            values = []

            try:
                for val in value:
                    values.append(self.db_field.rel.to.objects.get(pk=val))
            except self.db_field.rel.to.DoesNotExist:
                raise ValidationError(self.error_messages['invalid_choice'] % {'value': val})

            return values

        try:
            value = self.db_field.rel.to.objects.get(pk=int(value))
        except self.db_field.rel.to.DoesNotExist:
            raise ValidationError(self.error_messages['invalid_choice'] % {'value': value})

        return value

class RGBImageField(fields.ImageField):
    "Check that uploaded image is RGB"
#    widget = AdminFileWidget
    widget = widgets.FlashImageWidget

    def clean(self, data, initial=None):
        f = super(RGBImageField, self).clean(data, initial)

        if f is None:
            return None
        elif not data and initial:
            return initial

        if hasattr(data, 'temporary_file_path'):
            file = data.temporary_file_path()
        else:
            if hasattr(data, 'read'):
                file = StringIO(data.read())
            else:
                file = StringIO(data['content'])

        trial_image = Image.open(file)

        if trial_image.mode == 'CMYK':
            raise ValidationError(_('This image has a CMYK color profile. We can\'t work with CMYK. Please convert it to RGB.'))

        if hasattr(f, 'seek') and callable(f.seek):
            f.seek(0)
        return f

class CategoryChoiceField(ModelChoiceField):
    """ Category choice field. Choices restricted accordingly to CategoryUserRole. """

    def __init__(self, queryset, empty_label=u"---------", cache_choices=False,
                 required=True, widget=None, label=None, initial=None,
                 help_text=None, to_field_name=None, *args, **kwargs):
        kwargs.update({
            'queryset': queryset,
            'empty_label': empty_label,
            'cache_choices': cache_choices,
            'required': required,
            'widget': widget,
            'label': label,
            'initial': initial,
            'help_text': help_text,
            'to_field_name': to_field_name
        })
        if not('user' in kwargs and 'model' in kwargs):
            raise AttributeError('CategoryChoiceField requires user and model instances to be present in kwargs')
        self.model = kwargs.pop('model')
        self.user = kwargs.pop('user')
        super(CategoryChoiceField, self).__init__(*args, **kwargs)
        self.queryset = queryset
        #self.choice_cache = None

    def _get_queryset(self):
        if hasattr(self._queryset, '_newman_filtered'):
            return self._queryset
        view_perm = get_permission('view', self.model)
        change_perm = get_permission('change', self.model)
        perms = (view_perm, change_perm,)
        qs = permission_filtered_model_qs(self._queryset, self.user, perms)
        # user category filter
        qs = utils.user_category_filter(qs, self.user)
        qs._newman_filtered = True #magic variable
        self._set_queryset(qs)
        return self._queryset

    def _set_queryset(self, queryset):
        self._queryset = queryset
        self.widget.choices = self.choices

    queryset = property(_get_queryset, _set_queryset)

    def clean(self, value):
        cvalue = super(CategoryChoiceField, self).clean(value)
        return cvalue
        # TODO unable to realize if field was modified or not (when user has view permission a hits Save.)
        #      Permissions checks are placed in FormSets for now. CategoryChoiceField restricts category
        #      choices at the moment.
        # next part is category-based permissions (only for objects with category field)
        # attempt: to do role-permission checks here (add new and change permissions checking)
        # Adding new object
        #TODO check wheter field was modified or not.
        add_perm = get_permission('add', self.model)
        if not has_category_permission(self.user, cvalue, add_perm):
            raise ValidationError(_('Category not permitted'))
        # Changing existing object
        change_perm = get_permission('change', self.model)
        if not has_category_permission(self.user, cvalue, change_perm):
            raise ValidationError(_('Category not permitted'))
        return cvalue
