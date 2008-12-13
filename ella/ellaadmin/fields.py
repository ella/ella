import Image
from StringIO import StringIO

from django.forms import fields
from django.forms.util import ValidationError
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _

from ella.ellaadmin import widgets


class OnlyRGBImageField(fields.ImageField):
    "Check that uploaded image is RGB"

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

class RichTextAreaField(fields.Field):
    widget = widgets.RichTextAreaWidget
    default_error_messages = {
        'syntax_error': _('Bad syntax in markdown formatting or template tags.'),
        'url_error':  _('Some links are invalid: %s.'),
        'link_error':  _('Some links are broken: %s.'),
}

    def __init__(self, *args, **kwargs):
        super(RichTextAreaField, self).__init__(*args, **kwargs)

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

    def clean(self, value):
        "Validates markdown and temlate (box) syntax, validates links and check if exists."

        super(RichTextAreaField, self).clean(value)
        if value in fields.EMPTY_VALUES:
            return u''
        value = smart_unicode(value)

        # validate markdown links
        # commented out due to incomplete specs, will probably be replaced by JS validation

        #l = re.compile('\[.+\]\((.+)\)')
        #self.invalid_links = []
        #self.broken_links  = []
        #l.sub(self._check_url, value)

        #i = self.error_messages['url_error'] % ', '.join(self.invalid_links)
        #b = self.error_messages['link_error'] % ', '.join(self.broken_links)
        #if self.invalid_links and self.broken_links:
        #    raise ValidationError("%s %s" % (i, b))
        #elif self.invalid_links:
        #    raise ValidationError(i)
        #elif self.broken_links:
        #    raise ValidationError(b)

        # test render template
        try:
            from ella.core.templatetags.core import render_str
            render_str(value)
        except:
            raise ValidationError(self.error_messages['syntax_error'])

        return value

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
