from datetime import datetime
from os import path

from django.template.defaultfilters import slugify
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.conf import settings




from ella.db import fields
from ella.core.box import Box
from ella.photos.models import Photo
from ella.db.models import Publishable
from ella.core.models import Author, Source, Category

from nc.cdnclient.models import MediaField

class MediaBox(Box):
    def get_context(self):
        "Updates box context with media-specific variables."
        cont = super(MediaBox, self).get_context()
        cont.update({
                'title' : self.params.get('title', self.obj.title),
                'alt' : self.params.get('alt', ''),
})
        return cont

class Media(Publishable, models.Model):
    title = models.CharField(_('Title'), max_length=255)
    slug = models.SlugField(_('Slug'), max_length=255)
    photo = models.ForeignKey(Photo, verbose_name=_('Preview image'), null=True, blank=True, related_name='photo')
    file = MediaField()

    # Authors and Sources
    authors = models.ManyToManyField(Author, verbose_name=_('Authors'))
    source = models.ForeignKey(Source, blank=True, null=True, verbose_name=_('Source'))
    category = models.ForeignKey(Category, verbose_name=_('Category'), null=True)

    # content
    description = models.TextField(_('Description'), blank=True)
    text = models.TextField(_('Content'), blank=True)
    uploaded = models.DateTimeField(default=datetime.now, editable=False)

    def Box(self, box_type, nodelist):
        return MediaBox(self, box_type, nodelist)

    def __unicode__(self):
        return self.title

    def save(self):

        if (self.photo is None):
            file_name = Photo._meta.get_field_by_name('image')[0].get_directory_name() \
                      + 'screenshot-' + self.file.token
            self.file.create_thumb(settings.MEDIA_ROOT + file_name)
            photo = Photo()
            photo.title = "%s screenshot" % self.title
            photo.slug = slugify(photo.title)
            photo.image = file_name
            photo.width = 320
            photo.height = 240
            photo.save()
            self.photo = photo

        super(Media, self).save()

    class Meta:
        verbose_name = _('Media')
        verbose_name_plural = _('Media')


