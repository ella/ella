from datetime import datetime
from os import path

from django.utils.translation import ugettext_lazy as _
from django.db import models





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
    photo = models.ForeignKey(Photo, verbose_name=_('Preview image'), null=True, blank=True)
    file = MediaField()

    # Authors and Sources
    authors = models.ManyToManyField(Author, verbose_name=_('Authors'))
    source = models.ForeignKey(Source, blank=True, null=True, verbose_name=_('Source'))
    category = models.ForeignKey(Category, verbose_name=_('Category'), null=True)

    # content
    description = models.TextField(_('Description'), blank=True)
    text = models.TextField(_('Content'), blank=True)

    # stats
    created = models.DateTimeField(_('Created'), default=datetime.now, editable=False)
    updated = models.DateTimeField(_('Updated'), blank=True, null=True)

    def Box(self, box_type, nodelist):
        return MediaBox(self, box_type, nodelist)

    def __unicode__(self):
        return self.title


    class Meta:
        verbose_name = _('Media')
        verbose_name_plural = _('Media')

class Section(models.Model):
    media = models.ForeignKey(Media)

    title = models.CharField(_('Title'), max_length=255)
    description = models.TextField(_('Description'), blank=True)

    time = models.PositiveIntegerField(_('Start time in miliseconds'))
    duration = models.PositiveIntegerField(_('Duration in miliseconds'))

    def __unicode__(self):
        return 'Chapter %s' % self.title
