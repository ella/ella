from PIL import Image
import logging

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from django.forms import fields
from django.forms.util import ValidationError
from django.template import Template, TextNode, TemplateSyntaxError
from django.utils.translation import ugettext_lazy as _
from django.forms.models import ModelChoiceField, ModelMultipleChoiceField
from django.db.models.fields.related import ManyToManyField
from django.contrib.contenttypes.models import ContentType

from djangomarkup.fields import RichTextField, post_save_listener

from ella.core.templatetags.core import BoxNode, ObjectNotFoundOrInvalid
from ella.core.models import Dependency
from ella.newman import widgets, utils
from ella.newman.permission import get_permission, permission_filtered_model_qs, has_category_permission
from ella.newman.licenses.models import License

__all__ = [
    'NewmanRichTextField',
    'AdminSuggestField',
    'RGBImageField',
    'CategoryChoiceField',
    'ListingCustomField'
]

log = logging.getLogger('ella.newman')
DEP_SRC_TEXT_ATTR = '__dep_src_text'

def dependency_post_save_listener(sender, instance, **kwargs):
    src_texts = post_save_listener(sender, instance, src_text_attr=DEP_SRC_TEXT_ATTR)
    if not src_texts:
        return

    ct = ContentType.objects.get_for_model(instance)

    deps = list(Dependency.objects.filter(dependent_ct=ct, dependent_id=instance.pk))

    kw = {
        'dependent_ct': ct,
        'dependent_id': instance.pk,
    }

    # gather objects used id all texts
    objs = []
    for st in src_texts:
        content = getattr(instance, st.field)
        t = Template(content)
        objs.extend(box.get_obj() for box in t.nodelist.get_nodes_by_type(BoxNode))
    objs = set(objs)


    add = []
    for obj in objs:
        dep, created = Dependency.objects.get_or_create(
                target_ct=ContentType.objects.get_for_model(obj),
                target_id=obj.pk,
                **kw
            )
        if created:
            add.append(dep)
        else:
            deps.remove(dep)

    # delete outdated dependencies
    Dependency.objects.filter(pk__in=map(lambda d: d.pk, deps)).delete()

    if License._meta.installed:
        License.objects.reflect_added_dependencies(add)
        License.objects.reflect_removed_dependencies(deps)

class NewmanRichTextField(RichTextField):
    post_save_listener = staticmethod(dependency_post_save_listener)
    src_text_attr = DEP_SRC_TEXT_ATTR
    widget = widgets.NewmanRichTextAreaWidget

    default_error_messages = {
        'syntax_error': _('Bad syntax in syntax formatting or template tags.'),
        'invalid_object': _('Object does not exist or is not right inserted.'),
        'invalid_tag': _('You can use only box template tag.'),
    }

    def validate_rendered(self, rendered):
        """
        Validate that the target text composes only of text and boxes
        """
        try:
            t = Template(rendered)
        except TemplateSyntaxError, e:
            raise ValidationError(self.error_messages['syntax_error'])

        for n in t.nodelist:
            if isinstance(n, TextNode):
                continue
            elif isinstance(n, BoxNode):
                try:
                    o = n.get_obj()
                except ObjectNotFoundOrInvalid, e:
                    # TODO: pass lookup into error message
                    # this raises UnicodeEncodeError
                    # error_msg = self.error_messages['invalid_object'] % {
                    #    'model': n.model._meta.verbose_name,
                    #    'field': n.lookup[0],
                    #    'value': n.lookup[1]
                    #}
                    raise ValidationError(self.error_messages['invalid_object'])
            else:
                raise ValidationError(self.error_messages['invalid_tag'])


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

class ListingCustomField(ModelMultipleChoiceField):
    widget = widgets.ListingCustomWidget
    is_listing_custom_field = True

    def __init__(self, *args, **kwargs):
        super(ListingCustomField, self).__init__(*args, **kwargs)

class ChoiceCustomField(fields.CharField):
    widget = widgets.ChoiceCustomWidget
    is_choice_custom_field = True
    #default_text = u'%s' % (_('Click to edit option'))
    default_text = u''

    def __init__(self, *args, **kwargs):
        super(ChoiceCustomField, self).__init__(*args, **kwargs)

    def clean(self, value):
        cvalue = super(ChoiceCustomField, self).clean(value)
        return cvalue

class RawIdField(ModelChoiceField):

    def clean(self, value):

        if value not in fields.EMPTY_VALUES:
            try:
                value = int(value)
            except ValueError, e:
                raise ValidationError(self.error_messages['invalid_choice'])

        return super(RawIdField, self).clean(value)
