from django.forms import fields
from django.forms.util import ValidationError
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _

from ella.newman import widgets

class RichTextAreaField(fields.Field):
    widget = widgets.RichTextAreaWidget
    default_error_messages = {
        'syntax_error': _('Bad syntax in markdown formatting or template tags.'),
        'url_error':  _('Some links are invalid: %s.'),
        'link_error':  _('Some links are broken: %s.'),
}

    def __init__(self, *args, **kwargs):
        # TODO: inform widget about selected processor (JS editor..)
        super(RichTextAreaField, self).__init__(*args, **kwargs)

    def clean(self, value):

        super(RichTextAreaField, self).clean(value)
        if value in fields.EMPTY_VALUES:
            return u''
        value = smart_unicode(value)

        try:
            from ella.core.templatetags.core import render_str
            render_str(value)
        except:
            raise ValidationError(self.error_messages['syntax_error'])

        return value
