from django.db import models
from django.core.validators import ValidationError
import django.newforms as forms
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ImproperlyConfigured
from django.dispatch import dispatcher
from django.db.models import signals

class XMLMetaDataField(models.TextField):
    def __init__(self, verbose_name=None, name=None, schema_path=None, schema_type=None, **kwargs):
        self.schema_path = schema_path
        self.schema_type = schema_type
        models.TextField.__init__(self, verbose_name, name, **kwargs)

    def contribute_to_class(self, cls, name):
        super(XMLMetaDataField, self).contribute_to_class(cls, name)
        dispatcher.connect(self.get_schema_content, signal=signals.post_init, sender=cls)

    def get_schema_content(self, instance):
        if getattr(instance, self.attname):
            # TODO: cesta muze byt slozitejsi nez objekt.field, napr. 'source.type.metadata_schema'

#            pcs = self.schema_path.split('.')
#            for part in pcs:

            obj, field = self.schema_path.split('.',1)
            type = getattr(instance, obj)
            self.schema = getattr(type, field)

    def get_internal_type(self):
        return "TextField"

    def formfield(self, **kwargs):

        defaults = {'form_class': XMLFormField, 'schema': self.schema}
        defaults.update(kwargs)
        return super(XMLMetaDataField, self).formfield(**defaults)


class XMLFormField(forms.fields.Field):
    "FormField for XML. Validates well formed XML and validates against lxml (RelaxNG for now)"
    widget = forms.Textarea
    default_error_messages = {
        'syntax_error': _('Bad syntax:\n%s'),
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

        from StringIO import StringIO
        try:
            from lxml import etree
        except ImportError:
            raise ImproperlyConfigured, 'You need lxml and pyxml installed!'

        schema = StringIO(self.schema)

        relaxng_doc = etree.parse(schema)
        relaxng = etree.RelaxNG(relaxng_doc)
        log = relaxng.error_log

        doc = etree.parse(StringIO(value))
        if not relaxng(doc):
            raise ValidationError(self.error_messages['syntax_error'] % log)

        return value
