from datetime import datetime
from os import path

from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.conf import settings

from ella.db import fields
from ella.media.queue import QUEUE as ELLA_QUEUE


ACTIVE_MQ_HOST = getattr(settings, 'ACTIVE_MQ_HOST', None)


class RelaxXMLField(fields.XMLField):
    def get_schema_content(self, instance):
        fp = open("%s/relaxng.xml" % path.dirname(__file__), 'r')
        schema = fp.read()
        fp.close()
        return schema

class MetadataXMLField(fields.XMLField):
    def get_schema_content(self, instance):
        return instance.type.metadata_schema


class Type(models.Model):
    name = models.CharField(_('Type name'), max_length=80)
    extension = models.CharField(_('File extension'), max_length=10, blank=True,
            help_text=_('formatted file extension of this type will be changed to this value if given'))
    metadata_schema = models.TextField(_('Meta data schema'), blank=True,
            help_text=_('every media file validates its xml meta data to this schema'))

    def __unicode__(self):
        return self.name

class SourceManager(models.Manager):
    def create_from_queue(self, data):
        """create Source object"""
        data['type'] = Type.objects.get_or_create(name=data['type'])[0]
        data['slug'] = slugify(data['title'])
        source = self.create(**data)

        # pass all wanted formats to encoder
        for format in Format.objects.filter(from_type=source.type):
            formattedfile = dict(
                        source_hash = source.hash,
                        formatted_file_name = '%s-%s' % (source.hash, format),
                        source_file_type = format.from_type,
                        formatted_file_type = format.to_type,
                        format_name = format.name,
)
            ELLA_QUEUE.put('ella/media/encoder/formattedfile', formattedfile)

class Source(models.Model):
    title = models.CharField(_('Title'), max_length=255)
    slug = models.CharField(_('Slug'), db_index=True, max_length=255)
    hash = models.CharField(_('Content hash'), db_index=True, max_length=40)
    url = models.URLField(_('File url'), verify_exists=False, max_length=300)
    type = models.ForeignKey(Type, verbose_name=_('Type of this file'))
    metadata = models.TextField(_('Meta data'), blank=True,
            help_text=_('meta data xml - should be generated after file save'))

    description = models.TextField(_('Description'), blank=True)
    uploaded = models.DateTimeField(default=datetime.now, editable=False)

    objects = SourceManager()

    def __unicode__(self):
        return self.title

class FormatManager(models.Manager):
    def create_from_queue(data):
        # TODO: create format after updating any on encoder
        pass

class Format(models.Model):
    name = models.CharField(_('Format name'), max_length=80,
            help_text=_('this should be in some sluggy format'))
    from_type = models.ForeignKey(Type, related_name='format_from_set',
            verbose_name=_('From what type'))
    to_type = models.ForeignKey(Type, related_name='format_to_set',
            verbose_name=_('To what type'))

    objects = FormatManager()

    def __unicode__(self):
        return self.name

class FormattedFileManager(models.Manager):
    def create_from_queue(self, data):
        """create FormattedFile object"""
        data['source'] = Source.objects.get(hash=data['source'])
        data['format'] = Format.objects.get(name=data['format'])
        formattedfile = self.create(**data)

class FormattedFile(models.Model):
    source = models.ForeignKey(Source, verbose_name=_('Source file'))
    format = models.ForeignKey(Format, verbose_name=_('Format'))
    hash = models.CharField(_('Content hash'), db_index=True, max_length=40)
    url = models.URLField(_('File url'), verify_exists=False, max_length=300)
    metadata = models.TextField(_('Meta data'), blank=True,
            help_text=_('meta data xml - should be generated after file save'))
    status = models.IntegerField(_('Exit status'), blank=True, null=True)

    objects = FormattedFileManager()

    @property
    def type(self):
        return self.format.to_type

    class Meta:
        unique_together = (('source', 'format'),)

    def __unicode__(self):
        return "%s-%s" % (self.source.title, self.format.name)


# initialization
from ella.media import register
del register

