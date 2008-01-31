from django.db import models
from django.newforms.util import ValidationError
import django.newforms as forms
from django.utils.encoding import smart_unicode
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ImproperlyConfigured
from django.dispatch import dispatcher
from django.db.models import signals

class XMLField(models.TextField):
    def __init__(self, verbose_name=None, name=None, schema_type=None, **kwargs):
        self.schema_type = schema_type
        self.schema = ''
        models.TextField.__init__(self, verbose_name, name, **kwargs)

    def contribute_to_class(self, cls, name):
        super(XMLField, self).contribute_to_class(cls, name)
        dispatcher.connect(self._get_schema_content, signal=signals.pre_save, sender=cls)

    def _get_schema_content(self, instance):
        self.schema = self.get_schema_content(instance)

    def get_schema_content(self, instance):
        raise NotImplementedError, 'You must define this method.'

    def formfield(self, **kwargs):

        defaults = {'form_class': XMLFormField, 'schema': self.schema}
        defaults.update(kwargs)
        return super(XMLField, self).formfield(**defaults)


class XMLFormField(forms.fields.Field):
    "FormField for XML. Validates well formed XML and validates against lxml (RelaxNG for now)"
    widget = forms.Textarea
    default_error_messages = {
        'parse_schema_fail': _('Parse schema failed.'),
        'syntax_error': _('Bad syntax: %s'),
}

    def __init__(self, schema, *args, **kwargs):
        self.schema = schema
        super(XMLFormField, self).__init__(*args, **kwargs)

    def clean(self, value):
        "Validates XML against lxml."

        super(XMLFormField, self).clean(value)
        if value in forms.fields.EMPTY_VALUES:
            return u''
        value = smart_unicode(value)

        # FIXME: problem with pre_save signal(?), schema seems sometimes empty, but isn't
        if self.schema == '':
            return value

        from StringIO import StringIO
        try:
            from lxml import etree
        except ImportError:
            raise ImproperlyConfigured, 'You need lxml and pyxml installed!'

        schema = StringIO(self.schema)

        try:
            relaxng_doc = etree.parse(schema)
        except:
            raise ValidationError(self.error_messages['parse_schema_fail'])

        relaxng = etree.RelaxNG(relaxng_doc)

        from lxml.etree import XMLSyntaxError, DocumentInvalid

        try:
            doc = etree.parse(StringIO(value))
        except XMLSyntaxError, e:
            raise ValidationError(self.error_messages['syntax_error'] % e)

        try:
            relaxng.assertValid(doc)
        except DocumentInvalid, e:
            raise ValidationError(self.error_messages['syntax_error'] % e)

        return value
