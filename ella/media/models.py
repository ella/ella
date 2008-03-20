from datetime import datetime
from os import path

from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.conf import settings

from ella.db import fields
from ella.media.queue import QUEUE as ELLA_QUEUE
from ella.core.cache.utils import get_cached_object
from ella.core.box import Box
from ella.photos.models import Photo
from ella.db.models import Publishable
from ella.core.models import Author, Source, Category


ACTIVE_MQ_HOST = getattr(settings, 'ACTIVE_MQ_HOST', None)


class MediaBox(Box):
    def get_context(self):

        "Updates box context with media-specific variables."
        cont = super(MediaBox, self).get_context()
        cont.update({
                'formatted_files' : self.params.get('formatted_files', self.obj.formatted_files()),
                'title' : self.params.get('title', self.obj.title),
                'alt' : self.params.get('alt', ''),
})
        return cont

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

class MediaManager(models.Manager):
    def create_from_queue(self, data):
        """create Media (source) object"""
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


class Media(models.Model, Publishable):
    title = models.CharField(_('Title'), max_length=255)
    slug = models.CharField(_('Slug'), db_index=True, max_length=255)
    url = models.URLField(_('File url'), verify_exists=False, max_length=300)
    photo = models.ForeignKey(Photo, verbose_name=_('Preview image'), null=True, blank=True, related_name='photo')
    type = models.ForeignKey(Type, verbose_name=_('Type of this file'))
    hash = models.CharField(_('Content hash'), db_index=True, max_length=40)

    metadata = models.TextField(_('Meta data'), blank=True,
            help_text=_('meta data xml - should be generated after file save'))

    # Authors and Sources
    authors = models.ManyToManyField(Author, verbose_name=_('Authors'))
    source = models.ForeignKey(Source, blank=True, null=True, verbose_name=_('Source'))
    category = models.ForeignKey(Category, verbose_name=_('Category'), null=True)

    # content
    description = models.TextField(_('Description'), blank=True)
    content = models.TextField(_('Content'), blank=True)
    uploaded = models.DateTimeField(default=datetime.now, editable=False)

    objects = MediaManager()

    def formatted_files(self):
        return FormattedFile.objects.select_related().filter(source=self.id)

    def Box(self, box_type, nodelist):
        return MediaBox(self, box_type, nodelist)

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        if self.main_listing:
            return self.main_listing.get_absolute_url()

    class Meta:
        verbose_name = _('Media')
        verbose_name_plural = _('Media')


class FormatManager(models.Manager):
    def create_from_queue(self, data):
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
        data['source'] = Media.objects.get(hash=data['source'])
        data['format'] = Format.objects.get(name=data['format'])
        formattedfile = self.create(**data)

class FormattedFile(models.Model):
    source = models.ForeignKey(Media, verbose_name=_('Source file'))
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
        verbose_name = _('Formatted file')
        verbose_name_plural = _('Formatted files')

    def __unicode__(self):
        return "%s-%s" % (self.source.title, self.format.name)

# initialization
from ella.media import register
del register

