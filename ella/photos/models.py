from django.core.files.images import get_image_dimensions
import Image
from datetime import datetime
from os import path
import os

from django.db import models, IntegrityError
from django.conf import settings
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.sites.models import Site
from django.utils.safestring import mark_safe
from django.core.files.uploadedfile import UploadedFile

from ella.core.models.main import Author, Source
from ella.core.box import Box
from ella.core.cache.utils import get_cached_object
from ella.utils.filemanipulation import file_rename

from formatter import Formatter, detect_img_type

__all__ = ("Format", "FormatedPhoto", "Photo")

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
    box_class = PhotoBox
    title = models.CharField(_('Title'), max_length=200)
    description = models.TextField(_('Description'), blank=True)
    slug = models.SlugField(_('Slug'), max_length=255)
    image = models.ImageField(upload_to=UPLOAD_TO, height_field='height', width_field='width') # save it to YYYY/MM/DD structure
    width = models.PositiveIntegerField(editable=False)
    height = models.PositiveIntegerField(editable=False)

    # important area
    important_top = models.PositiveIntegerField(null=True, blank=True)
    important_left = models.PositiveIntegerField(null=True, blank=True)
    important_bottom = models.PositiveIntegerField(null=True, blank=True)
    important_right = models.PositiveIntegerField(null=True, blank=True)

    # Authors and Sources
    authors = models.ManyToManyField(Author, verbose_name=_('Authors') , related_name='photo_set')
    source = models.ForeignKey(Source, blank=True, null=True, verbose_name=_('Source'))

    created = models.DateTimeField(default=datetime.now, editable=False)

    def thumb(self):
        """
        Generates html and thumbnails for admin site.
        """
        thumbUrl = self.thumb_url()
        if not thumbUrl:
            return mark_safe("""<strong>%s</strong>""" % ugettext('Thumbnail not available'))
        return mark_safe("""<a href="%s"><img src="%s" alt="Thumbnail %s" /></a>""" % (self.image.url, thumbUrl, self.title))
    thumb.allow_tags = True

    def get_thumbnail_path(self, image_name=None):
        """
        Return relative path for thumbnail file for storage
        photos/2008/12/31/foo.jpg => photos/2008/12/31/thumb-foo.jpg
        """
        if not image_name:
            image_name = self.image.name
        return path.dirname(image_name) + "/" + 'thumb-%s' % path.basename(image_name)

    def thumb_url(self):
        """
        Generates thumbnail for admin site and returns its url
        """
        type = detect_img_type(self.image.path)
        if not type:
            return None

        
        thumb_name = self.get_thumbnail_path()

        storage = self.image.storage
        if not storage.exists(thumb_name):
            try:
                im = Image.open(self.image.path)
                im.thumbnail(PHOTOS_THUMB_DIMENSION, Image.ANTIALIAS)
                im.save(storage.path(thumb_name), type)
            except IOError:
                # TODO Logging something wrong
                return None
        return storage.url(thumb_name)

    def save(self, force_insert=False, force_update=False):
        """Overrides models.Model.save.

        - Generates slug.
        - Saves image file.
        """

        # prefill the slug with the ID, it requires double save
        if not self.id:
            if isinstance(self.image, UploadedFile):
                # due to PIL has read several bytes from image, position in file has to be reset
                self.image.seek(0)
            super(Photo, self).save(force_insert, force_update)
            self.width, self.height = get_image_dimensions(self.image.path)
            self.slug = str(self.id) + '-' + self.slug
            force_insert, force_update = False, True
            image_changed = False
        else:
            old = Photo.objects.get(pk = self.pk)
            image_changed = old.image != self.image
        # rename image by slug
        imageType = detect_img_type(self.image.path)
        if imageType is not None:
            self.image = file_rename(self.image.name, self.slug, PHOTOS_TYPE_EXTENSION[ imageType ])
        # delete formatedphotos if new image was uploaded
        if image_changed:
            super(Photo, self).save(force_insert, force_update)
            self.width, self.height = get_image_dimensions(self.image.path)
            force_insert, force_update = False, True
            for f_photo in self.formatedphoto_set.all():
                f_photo.delete()
        super(Photo, self).save(force_insert, force_update)

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
        return self.image.url

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
                                                                                 'or the formatted photo can vary from max_height for flexible_max_height.')))
    flexible_max_height = models.PositiveIntegerField(_('Flexible max height'), blank=True, null=True)
    stretch = models.BooleanField(_('Stretch'))
    nocrop = models.BooleanField(_('Do not crop'))
    resample_quality = models.IntegerField(_('Resample quality'), choices=PHOTOS_FORMAT_QUALITY, default=85)
    sites = models.ManyToManyField(Site, verbose_name=_('Sites'))

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

    @property
    def url(self):
        "Returns url of the photo file."
        if not PHOTOS_DO_URL_CHECK:
            return settings.MEDIA_URL + self.filename

        if not path.exists(settings.MEDIA_ROOT):
            # NFS not available - we have no chance of creating it
            return self.format.get_blank_img()['url']

        if path.exists(path.join(settings.MEDIA_ROOT, self.filename)):
            # image exists
            return settings.MEDIA_URL + self.filename

        # image does not exist - try and create it
        try:
            self.generate()
            return settings.MEDIA_URL + self.filename
        except (IOError, SystemError):
            return self.format.get_blank_img()['url']


    def generate(self):
        "Generates photo file in current format"
        crop_box = None
        if self.crop_left:
            crop_box = (self.crop_left, self.crop_top, \
                    self.crop_left + self.crop_width, self.crop_top + self.crop_height)

        important_box = None
        if self.photo.important_top:
            p = self.photo
            important_box = (p.important_left, p.important_top, p.important_right, p.important_bottom)

        formatter = Formatter(Image.open(self.filename), self.format, crop_box=crop_box, important_box=important_box)

        stretched_photo, crop_box = formatter.format()
        self.width, self.height = stretched_photo.size
        self.filename = self.file(relative=True)
        stretched_photo.save(self.file(), quality=self.format.resample_quality)

    def save(self, force_insert=False, force_update=False):
        """Overrides models.Model.save

        - Removes old file from the FS
        - Generates new file.
        """
        self.remove_file()
        self.generate()
        super(FormatedPhoto, self).save(force_insert, force_update)

    def delete(self):
        self.remove_file()
        super(FormatedPhoto, self).delete()

    def remove_file(self):
        if path.exists(path.join(settings.MEDIA_ROOT, self.file(relative=True))):
            os.remove(path.join(settings.MEDIA_ROOT, self.file(relative=True)))

    def file(self, relative=False):
        """ Method returns formated photo path - derived from format.id and source Photo filename """
        if relative:
            source_file = path.split(self.photo.image.name)
        else:
            source_file = path.split(self.photo.image.path)
        return path.join(source_file[0],  str (self.format.id) + '-' + source_file[1])

    def __unicode__(self):
        return u"%s - %s" % (self.filename, self.format)

    class Meta:
        verbose_name = _('Formated photo')
        verbose_name_plural = _('Formated photos')
        unique_together = (('photo','format'),)

