from widgets import RichTextAreaWidget

from django.newforms import fields
from django.newforms.util import ValidationError
from django.utils.encoding import smart_unicode
from django.utils.translation import gettext_lazy as _

from ella.core.templatetags.core import render_str


class RichTextAreaField(fields.Field):
    widget = RichTextAreaWidget
    default_error_messages = {
        'syntax_error': _('Bad syntax in markdown formatting or template tags.'),
}

    def __init__(self, *args, **kwargs):
        super(RichTextAreaField, self).__init__(*args, **kwargs)

    def clean(self, value):
        "Validates markdown and temlate (box) syntax."

        super(RichTextAreaField, self).clean(value)
        if value in fields.EMPTY_VALUES:
            return u''
        value = smart_unicode(value)


        try:
            render_str(value)
        except:
            raise ValidationError(self.error_messages['syntax_error'])

        return value
