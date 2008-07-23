from datetime import datetime
from os import path

from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.conf import settings

from ella.db import fields
from ella.core.box import Box
from ella.photos.models import Photo
from ella.db.models import Publishable
from ella.core.models import Author, Source, Category


class RelaxXMLField(fields.XMLField):
    def get_schema_content(self, instance):
        fp = open("%s/relaxng.xml" % path.dirname(__file__), 'r')
        schema = fp.read()
        fp.close()
        return schema

class MetadataXMLField(fields.XMLField):
    def get_schema_content(self, instance):
        return instance.type.metadata_schema





class MediaBox(Box):
    def get_context(self):
        "Updates box context with media-specific variables."
        cont = super(MediaBox, self).get_context()
        cont.update({
                'formatted_media' : self.params.get('formatted_media', self.obj.formatted_media()),
                'title' : self.params.get('title', self.obj.title),
                'alt' : self.params.get('alt', ''),
})
        return cont

class Media(Publishable, models.Model):
    title = models.CharField(_('Title'), max_length=255)
    slug = models.SlugField(_('Slug'), max_length=255)
    url = models.URLField(_('File URL'), verify_exists=False, max_length=300, blank=True)
    photo = models.ForeignKey(Photo, verbose_name=_('Preview image'), null=True, blank=True, related_name='photo')
    hash = models.CharField(_('Content hash'), db_index=True, max_length=50, blank=True)

    metadata = models.TextField(_('Meta data'), blank=True,
            help_text=_('meta data xml - should be generated after file save'))

    # Authors and Sources
    authors = models.ManyToManyField(Author, verbose_name=_('Authors'))
    source = models.ForeignKey(Source, blank=True, null=True, verbose_name=_('Source'))
    category = models.ForeignKey(Category, verbose_name=_('Category'), null=True)

    # content
    description = models.TextField(_('Description'), blank=True)
    text = models.TextField(_('Content'), blank=True)
    uploaded = models.DateTimeField(default=datetime.now, editable=False)

    def formatted_media(self):
        return FormattedMedia.objects.select_related().filter(source=self.id)

    def Box(self, box_type, nodelist):
        return MediaBox(self, box_type, nodelist)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('Media')
        verbose_name_plural = _('Media')




class Format(models.Model):
    name = models.CharField(_('Format name'), max_length=80,
            help_text=_('this should be in some sluggy format'))

    def __unicode__(self):
        return self.name

class FormattedMedia(models.Model):
    source = models.ForeignKey(Media, verbose_name=_('Source file'))
    format = models.ForeignKey(Format, verbose_name=_('Format'))
    hash = models.CharField(_('Content hash'), db_index=True, max_length=50, blank=True)
    url = models.URLField(_('File url'), verify_exists=False, max_length=300, blank=True)
    metadata = models.TextField(_('Meta data'), blank=True,
            help_text=_('meta data xml - should be generated after file save'))
    status = models.IntegerField(_('Exit status'), blank=True, null=True)

    class Meta:
        unique_together = (('source', 'format'),)
        verbose_name = _('Formatted file')
        verbose_name_plural = _('Formatted files')

    def __unicode__(self):
        return "%s - %s" % (self.source.title, self.format.name)

# initialization
from ella.media import register
del register

