from PIL import Image
from StringIO import StringIO

from django.forms import fields
from django.forms.models import ModelMultipleChoiceField
from django.forms.util import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.template import Template, TextNode, TemplateSyntaxError
from django.contrib.admin.widgets import AdminFileWidget
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from ella.core.models import Dependency
from ella.ellaadmin import widgets


DEP_SRC_TEXT_ATTR = '__dep_src_text'

class OnlyRGBImageField(fields.ImageField):
    "Check that uploaded image is RGB"
    widget = AdminFileWidget

    def clean(self, data, initial=None):
        f = super(OnlyRGBImageField, self).clean(data, initial)

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

if 'ella.newman' in settings.INSTALLED_APPS:
    def dependency_post_save_listener(sender, instance, **kwargs):
        from ella.core.templatetags.core import BoxNode
        from ella.newman.licenses.models import License
        from djangomarkup.fields import post_save_listener
        
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

    from djangomarkup.fields import RichTextField
    class RichTextAreaField(RichTextField):
        post_save_listener = staticmethod(dependency_post_save_listener)
        src_text_attr = DEP_SRC_TEXT_ATTR
        #post_save_listener = staticmethod(post_save_listener)
        widget = widgets.RichTextAreaWidget
        default_error_messages = {
            'syntax_error': _('Bad syntax in markdown formatting or template tags.'),
            'invalid_object': _('Object does not exist or is not right inserted.'),
            'invalid_tag': _('You can use only box template tag.'),
            'url_error':  _('Some links are invalid: %s.'),
            'link_error':  _('Some links are broken: %s.'),
        }
    
        def validate_rendered(self, rendered):
            """
            Validate that the target text composes only of text and boxes
            """
            from ella.core.templatetags.core import BoxNode, ObjectNotFoundOrInvalid
    
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
    
        def _check_url(self, match):
    
            # FIXME: (?) I have problem testing development urls (future listngs) http://localhost:3000/...
    
            link = match.group(1)
    
            import urllib2
            headers = {
                "Accept": "text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5",
                "Accept-Language": "en-us,en;q=0.5",
                "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
                "Connection": "close",
                "User-Agent": fields.URL_VALIDATOR_USER_AGENT,
            }
    
            try:
                req = urllib2.Request(link, None, headers)
                urllib2.urlopen(req)
            except ValueError:
                self.invalid_links.append(link)
            except:
    
                # try with GET parameter "ift=t" for our objects with future listing
                if '?' in link:
                    tlink = link + '&ift=t'
                else:
                    tlink = link + '?ift=t'
    
                try:
                    req = urllib2.Request(tlink, None, headers)
                    urllib2.urlopen(req)
                except:
                    self.broken_links.append(link)

class GenericSuggestField(fields.ChoiceField):

    def __init__(self, data=[], **kwargs):
        # i need db_field for blank/required and label, maybe not
        self.db_field, self.model, self.lookups = data
        self.widget = widgets.GenericSuggestAdminWidget(data, **kwargs)
        super(GenericSuggestField, self).__init__(data, **kwargs)

    def clean(self, value):
        if self.required and value in fields.EMPTY_VALUES:
            raise ValidationError(self.error_messages['required'])
        elif value in fields.EMPTY_VALUES:
            return None

        value = int(value)

        try:
            value = self.db_field.rel.to.objects.get(pk=value)
        except self.db_field.rel.to.DoesNotExist:
            raise ValidationError(self.error_messages['invalid_choice'] % {'value': value})

        return value

class GenericSuggestFieldMultiple(fields.MultipleChoiceField):

    def __init__(self, data=[], **kwargs):
        # i need db_field for blank/required and label, maybe not
        self.db_field, self.model, self.lookups = data
        self.widget = widgets.GenericSuggestAdminWidgetMultiple(data, **kwargs)
        super(GenericSuggestFieldMultiple, self).__init__(data, **kwargs)

    def clean(self, value):
        if self.required and value in fields.EMPTY_VALUES:
            raise ValidationError(self.error_messages['required'])
        elif value in fields.EMPTY_VALUES:
            return []

        value = [int(v) for v in value.split(',')]
        if not isinstance(value, (list, tuple)):
            raise ValidationError(self.error_messages['invalid_list'])

        values = []

        # Validate that each value
        try:
            for val in value:
                values.append(self.db_field.rel.to.objects.get(pk=val))
        except self.db_field.rel.to.DoesNotExist:
            raise ValidationError(self.error_messages['invalid_choice'] % {'value': val})

        return values

class ListingCustomField(ModelMultipleChoiceField):
    widget = widgets.ListingCustomWidget
    #widget = widgets.ListingCategoryWidget
    is_listing_custom_field = True

    def __init__(self, *args, **kwargs):
        super(ListingCustomField, self).__init__(*args, **kwargs)

