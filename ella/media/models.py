from datetime import datetime

from django.utils.translation import ugettext_lazy as _
from django.db import models

from ella.core.box import Box
from ella.photos.models import Photo
from ella.core.models import Publishable
from ella.core.models import Author, Source, Category

from nc.cdnclient.models import MediaField


class MediaTime(int):
    """
    Time in miliseconds

    Like int type with seconds method (because you often need time seconds)
    """
    def seconds(self):
        return float(self) / 1000

class MediaTimeField(models.PositiveIntegerField):
    """
    Like PositiveIntegerField but returns MediaTime instead of int
    """
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if value == "" or value is None:
            return None
        elif isinstance(value, MediaTime):
            return value
        else:
            return MediaTime(value)

class MediaBox(Box):
    def get_context(self):
        "Updates box context with media-specific variables."
        cont = super(MediaBox, self).get_context()
        cont.update({
                'title' : self.params.get('title', self.obj.title),
                'alt' : self.params.get('alt', ''),
            })
        return cont

class Media(Publishable):
    """
    Media object

    Build around nc.cdnclient.models.MediaField and adds fields like title, photo,...
    """
    box_class = MediaBox
    file = MediaField()

    # content
    text = models.TextField(_('Content'), blank=True)

    # stats
    created = models.DateTimeField(_('Created'), default=datetime.now, editable=False)
    updated = models.DateTimeField(_('Updated'), blank=True, null=True)

    def get_sections(self):
        """
        Returns sections (chapters) for this media
        """
        return self.section_set.all()

    def get_usage(self):
        """
        Returns sites where media is used
        """
        return self.usage_set.all().order_by('-priority')

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('Media')
        verbose_name_plural = _('Media')

class Section(models.Model):
    """
    Represents section (chapter) in media
    """
    media = models.ForeignKey(Media)

    title = models.CharField(_('Title'), max_length=255)
    description = models.TextField(_('Description'), blank=True)

    time = MediaTimeField(_('Start time in miliseconds'))
    duration = MediaTimeField(_('Duration in miliseconds'), blank=True, null=True)

    class Meta:
        ordering = ('id',)

    def __unicode__(self):
        return 'Chapter %s' % self.title

class Usage(models.Model):
    """
    Sites where media is used
    """
    media = models.ForeignKey(Media)

    title = models.CharField(_('Title'), max_length=255)
    url = models.URLField(_('Url'), max_length=255)
    priority = models.SmallIntegerField(_('Priority'))
