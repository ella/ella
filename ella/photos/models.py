import Image
from datetime import datetime
from os import path
from imageop import ImageStretch, detect_img_type
import os

from django.db import models, transaction, IntegrityError
from django.conf import settings
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.contenttypes import generic
from django.contrib.sites.models import Site
from django.utils.safestring import mark_safe

from ella.core.models import Author, Source
from ella.core.managers import RelatedManager
from ella.core.box import Box
from ella.core.cache.utils import get_cached_object
from ella.utils.filemanipulation import file_rename
from ella.tagging.models import TaggedItem

# settings default
PHOTOS_FORMAT_QUALITY_DEFAULT = (
    (45, _('Low')),
    (65, _('Medium')),
    (75, _('Good')),
    (85, _('Better')),
    (95, _('High')),
)

PHOTOS_THUMB_DIMENSION_DEFAULT = (80,80)

PHOTOS_FORMAT_QUALITY = getattr(settings, 'PHOTOS_FORMAT_QUALITY', PHOTOS_FORMAT_QUALITY_DEFAULT)
PHOTOS_THUMB_DIMENSION = getattr(settings, 'PHOTOS_THUMB_DIMENSION', PHOTOS_THUMB_DIMENSION_DEFAULT)
PHOTOS_DO_URL_CHECK = getattr(settings, 'PHOTOS_DO_URL_CHECK', False)
CUSTOM_SUBDIR = getattr(settings, 'PHOTOS_CUSTOM_SUBDIR', '')
UPLOAD_TO = CUSTOM_SUBDIR and 'photos/%s/%%Y/%%m/%%d' % CUSTOM_SUBDIR or 'photos/%Y/%m/%d'

PHOTOS_TYPE_EXTENSION = {
    'JPEG': '.jpg',
    'PNG': '.png',
    'GIF': '.gif'
}


class PhotoBox(Box):
    def get_context(self):
        "Updates box context with photo-specific variables."
        cont = super(PhotoBox, self).get_context()
        cont.update({
                'title' : self.params.get('title', self.obj.title),
                'alt' : self.params.get('alt', ''),
                'description' : self.params.get('description', self.obj.description),
                'show_title' : self.params.get('show_title', ''),
                'show_description' : self.params.get('show_description', ''),
                'show_authors' : self.params.get('show_authors', ''),
                'show_detail' : self.params.get('show_detail', ''),
                'link_url': self.params.get('link_url', ''),
})
        return cont

class Photo(models.Model):
    "Represents original (unformated) photo."
    title = models.CharField(_('Title'), max_length=200)
    description = models.TextField(_('Description'), blank=True)
    slug = models.SlugField(_('Slug'), max_length=255)
    image = models.ImageField(upload_to=UPLOAD_TO , height_field='height', width_field='width') # save it to YYYY/MM/DD structure
    width = models.PositiveIntegerField(editable=False)
    height = models.PositiveIntegerField(editable=False)

    # Authors and Sources
    authors = models.ManyToManyField(Author, verbose_name=_('Authors') , related_name='photo_set')
    source = models.ForeignKey(Source, blank=True, null=True, verbose_name=_('Source'))

    created = models.DateTimeField(default=datetime.now, editable=False)

    tags = generic.GenericRelation(TaggedItem)

    def thumb(self):
        """
        Generates html and thumbnails for admin site.
        """
        thumbUrl = self.thumb_url()
        if not thumbUrl:
            return mark_safe("""<strong>%s</strong>""" % ugettext('Thumbnail not available'))
        return mark_safe("""<a href="%s%s"><img src="%s%s" alt="Thumbnail %s" /></a>""" % (settings.MEDIA_URL, str(self.image).replace('\\', '/'), settings.MEDIA_URL, thumbUrl.replace('\\', '/'), self.title))
    thumb.allow_tags = True

    def thumb_url(self):
        spl = path.split(self.image)
        woExtension = spl[1].rsplit('.', 1)[0]
        imageType = detect_img_type(path.join(settings.MEDIA_ROOT, self.image))
        if not imageType:
            return None
        ext = PHOTOS_TYPE_EXTENSION[ imageType ]
        filename = 'thumb-%s%s' % (woExtension, ext)
        tPath = (spl[0] , filename)
        tinythumb = path.join(*tPath)
        tinythumbPath = path.join(settings.MEDIA_ROOT, tinythumb)
        if not path.exists(tinythumbPath):
            try:
                im = Image.open(path.join(settings.MEDIA_ROOT, self.image))
                im.thumbnail(PHOTOS_THUMB_DIMENSION , Image.ANTIALIAS)
                im.save(tinythumbPath, imageType)
            except IOError:
                # TODO Logging something wrong
                return None
        return tinythumb

    def Box(self, box_type, nodelist):
        return PhotoBox(self, box_type, nodelist)

    @transaction.commit_on_success
    def save(self):
        """Overrides models.Model.save.

        - Generates slug.
        - Saves image file.
        """
        # prefill the slug with the ID, it requires double save
        if not self.id:
            super(Photo, self).save()
            self.slug = str(self.id) + '-' + self.slug
        # rename image by slug
        imageType = detect_img_type(path.join(settings.MEDIA_ROOT, self.image))
        if imageType is not None:
            self.image = file_rename(self.image, self.slug, PHOTOS_TYPE_EXTENSION[ imageType ])
        super(Photo, self).save()

    def ratio(self):
        "Return photo's width to height ratio"
        if self.height:
            return float(self.width) / self.height
        else:
            return None

    def get_formated_photo(self, format):
        "Return formated photo"
        format_object = Format.objects.get(name=format, site=settings.SITE_ID)
        try:
            formated_photo = get_cached_object(FormatedPhoto, photo=self, format=format_object)
        except FormatedPhoto.DoesNotExist:
            try:
                formated_photo = FormatedPhoto.objects.create(photo=self, format=format_object)
            except (IOError, SystemError, IntegrityError):
                return None

        return formated_photo

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return self.get_image_url()

    class Meta:
        verbose_name = _('Photo')
        verbose_name_plural = _('Photos')
        ordering = ('-created',)


class Format(models.Model):
    "Defines per-site photo sizes"
    name = models.CharField(_('Name'), max_length=80)
    max_width = models.PositiveIntegerField(_('Max width'))
    max_height = models.PositiveIntegerField(_('Max height'))
    flexible_height = models.BooleanField(_('Flexible height'), help_text=_(('Determines whether max_height is an absolute maximum, '
                                                                                 'or the formatted photo can vary from max_height for flexible_max_height.'))
)
    flexible_max_height = models.PositiveIntegerField(_('Flexible max height'), blank=True, null=True)
    stretch = models.BooleanField(_('Stretch'))
    nocrop = models.BooleanField(_('Do not crop'))
    resample_quality = models.IntegerField(_('Resample quality'), choices=PHOTOS_FORMAT_QUALITY, default=85)
    site = models.ForeignKey(Site)

    def get_blank_img(self):
        """
        Return fake FormatedPhoto object to be used in templates when an error occurs in image generation.
        """
        out = {
            'width' : self.max_width,
            'height' : self.max_height,
            'filename' : 'img/empty/%s.png' % (self.name),
            'format' : self,
            'url' : settings.MEDIA_URL + 'img/empty/%s.png' % (self.name),
}
        return out

    def ratio(self):
        "Return photo's width to height ratio"
        return float(self.max_width) / self.max_height

    def __unicode__(self):
        return  u"%s (%sx%s) " % (self.name, self.max_width, self.max_height)

    class Meta:
        verbose_name = _('Format')
        verbose_name_plural = _('Formats')
        ordering = ('name', '-max_width',)


class FormatedPhoto(models.Model):
    "Specific photo of specific format."
    photo = models.ForeignKey(Photo)
    format = models.ForeignKey(Format)
    filename = models.CharField(max_length=300, editable=False) # derive local filename and url
    crop_left = models.PositiveIntegerField()
    crop_top = models.PositiveIntegerField()
    crop_width = models.PositiveIntegerField()
    crop_height = models.PositiveIntegerField()
    width = models.PositiveIntegerField(editable=False)
    height = models.PositiveIntegerField(editable=False)

    objects = RelatedManager()

    @property
    def url(self):
        "Returns url of the photo file."
        if not PHOTOS_DO_URL_CHECK:
            return settings.MEDIA_URL + str(self.filename).replace('\\', '/')

        if not path.exists(settings.MEDIA_ROOT):
            # NFS not available - we have no chance of creating it
            return self.format.get_blank_img()['url']

        if path.exists(path.join(settings.MEDIA_ROOT, self.filename)):
            # image exists
            return settings.MEDIA_URL + str(self.filename).replace('\\', '/')

        # image does not exist - try and create it
        try:
            self.generate()
            return settings.MEDIA_URL + self.filename
        except (IOError, SystemError):
            return self.format.get_blank_img()['url']


    def generate(self):
        "Generates photo file in current format"
        i = ImageStretch(filename=self.photo.get_image_filename(), formated_photo=self)
        stretched_photo = i.stretch_image()
        self.width, self.height = stretched_photo.size
        self.filename = self.file(relative=True)
        stretched_photo.save(self.file(), quality=self.format.resample_quality)

    def save(self):
        """Overrides models.Model.save

        - Removes old file from the FS
        - Generates new file.
        """
        if path.exists(path.join(settings.MEDIA_ROOT, self.file(relative=True))):
            os.remove(path.join(settings.MEDIA_ROOT, self.file(relative=True)))
        self.generate()
        super(FormatedPhoto, self).save()

    def file(self, relative=False):
        """ Method returns formated photo path - derived from format.id and source Photo filename """
        if relative:
            source_file = path.split(self.photo.image)
        else:
            source_file = path.split(self.photo.get_image_filename())
        return path.join(source_file[0],  str (self.format.id) + '-' + source_file[1])

    def __unicode__(self):
        return u"%s - %s" % (self.filename, self.format)

    class Meta:
        verbose_name = _('Formated photo')
        verbose_name_plural = _('Formated photos')
        unique_together = (('photo','format'),)

