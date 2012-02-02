import logging
from PIL import Image
from datetime import datetime
from os import path
from cStringIO import StringIO
import os.path

from django.db import models, IntegrityError
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_unicode, smart_str
from django.contrib.sites.models import Site
from django.core.files.base import ContentFile
from django.conf import settings
from django.template.defaultfilters import slugify

from jsonfield.fields import JSONField

from ella.core.models.main import Author, Source
from ella.core.box import Box
from ella.core.cache.utils import get_cached_object
from ella.photos.conf import photos_settings

from formatter import Formatter

__all__ = ("Format", "FormatedPhoto", "Photo")

log = logging.getLogger('ella.photos')

redis = None
REDIS_PHOTO_KEY = 'photo:%d'
REDIS_FORMATTED_PHOTO_KEY = 'photo:%d:%d'

if hasattr(settings, 'PHOTOS_REDIS'):
    try:
        from redis import Redis
    except:
        log.error('Redis support requested but Redis client not installed.')
        redis = None
    else:
        redis = Redis(**getattr(settings, 'PHOTOS_REDIS'))

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
                'show_source' : self.params.get('show_source', ''),###
                'link_url': self.params.get('link_url', ''),
            })
        return cont

def upload_to(instance, filename):
    name, ext = os.path.splitext(filename)
    if instance.slug:
        name = instance.slug
    ext = photos_settings.TYPE_EXTENSION.get(instance._get_image().format, ext.lower())

    return os.path.join(
        force_unicode(datetime.now().strftime(smart_str(photos_settings.UPLOAD_TO))),
        name + ext
    )

class Photo(models.Model):
    "Represents original (unformated) photo."
    box_class = PhotoBox
    title = models.CharField(_('Title'), max_length=200)
    description = models.TextField(_('Description'), blank=True)
    slug = models.SlugField(_('Slug'), max_length=255)
    image = models.ImageField(_('Image'), upload_to=upload_to, height_field='height', width_field='width') # save it to YYYY/MM/DD structure
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

    # generic JSON field to store app cpecific data
    app_data = JSONField(default='{}', blank=True, editable=False)

    def get_image_info(self):
        return {
            'url': self.image.url,
            'width': self.width,
            'height': self.height,
        }

    def _get_image(self):
        if not hasattr(self, '_pil_image'):
            self._pil_image = Image.open(self.image)
        return self._pil_image

    def save(self, **kwargs):
        """Overrides models.Model.save.

        - Generates slug.
        - Saves image file.
        """
        if not self.width or not self.height:
            self.width, self.height = self.image.width, self.image.height

        # prefill the slug with the ID, it requires double save
        if not self.id:
            img = self.image

            # store dummy values first...
            w, h = self.width, self.height
            self.image = ''
            self.width, self.height = w, h
            self.slug = ''

            super(Photo, self).save(force_insert=True)

            # ... so that we can generate the slug
            self.slug = str(self.id) + '-' + slugify(self.title)
            # truncate slug in order to fit in an ImageField and/or paths in Redirects
            self.slug = self.slug[:64]
            # .. tha will be used in the image's upload_to function
            self.image = img
            # and the image will be saved properly
            super(Photo, self).save(force_update=True)
        else:
            old = Photo.objects.get(pk=self.pk)

            # delete formatedphotos if new image was uploaded
            if old.image != self.image:
                for f_photo in self.formatedphoto_set.all():
                    f_photo.delete()

            super(Photo, self).save(force_update=True)

        if redis:
            redis.hmset(REDIS_PHOTO_KEY % self.pk, self.get_image_info())

    def delete(self, *args, **kwargs):
        if redis:
            redis.delete(REDIS_PHOTO_KEY % self.id)
        super(Photo, self).delete(*args, **kwargs)

    def ratio(self):
        "Return photo's width to height ratio"
        if self.height:
            return float(self.width) / self.height
        else:
            return None

    def get_formated_photo(self, format):
        "Return formated photo"
        return FormatedPhoto.objects.get_photo_in_format(self, format)

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return self.image.url

    class Meta:
        verbose_name = _('Photo')
        verbose_name_plural = _('Photos')

FORMAT_CACHE = {}
class FormatManager(models.Manager):
    def get_for_name(self, name):
        try:
            return FORMAT_CACHE[name]
        except KeyError:
            FORMAT_CACHE[name] = format = get_cached_object(Format, name=name, sites__id=settings.SITE_ID)
        return format

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
    resample_quality = models.IntegerField(_('Resample quality'), choices=photos_settings.FORMAT_QUALITY, default=85)
    sites = models.ManyToManyField(Site, verbose_name=_('Sites'))

    objects = FormatManager()

    def get_blank_img(self):
        """
        Return fake FormatedPhoto object to be used in templates when an error occurs in image generation.
        """
        out = {
            'blank': True,
            'width' : self.max_width,
            'height' : self.max_height,
            'url' : photos_settings.EMPTY_IMAGE_SITE_PREFIX + 'img/empty/%s.png' % (self.name),
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


class FormatedPhotoManager(models.Manager):
    def get_photo_in_format(self, photo, format):
        if isinstance(photo, Photo):
            photo_id = photo.id
        else:
            photo_id = photo
            photo = None

        if not isinstance(format, Format):
            format = Format.objects.get_for_name(format)

        if redis:
            p = redis.pipeline()
            p.hgetall(REDIS_PHOTO_KEY % photo_id)
            p.hgetall(REDIS_FORMATTED_PHOTO_KEY % (photo_id, format.id))
            original, formatted = p.execute()
            if formatted:
                formatted['original'] = original
                return formatted

        if not photo:
            try:
                photo = get_cached_object(Photo, pk=photo_id)
            except Photo.DoesNotExist:
                return format.get_blank_img()

        try:
            formated_photo = get_cached_object(FormatedPhoto, photo=photo, format=format)
        except FormatedPhoto.DoesNotExist:
            try:
                formated_photo = self.create(photo=photo, format=format)
            except (IOError, SystemError, IntegrityError), e:
                log.error("Cannot create formatted photo.", e)
                return format.get_blank_img()

        return {
            'original': photo.get_image_info(),

            'url': formated_photo.url,
            'width': formated_photo.width,
            'height': formated_photo.height,
        }


class FormatedPhoto(models.Model):
    "Specific photo of specific format."
    photo = models.ForeignKey(Photo)
    format = models.ForeignKey(Format)
    image = models.ImageField(upload_to=photos_settings.UPLOAD_TO, height_field='height', width_field='width', max_length=300) # save it to YYYY/MM/DD structure
    crop_left = models.PositiveIntegerField()
    crop_top = models.PositiveIntegerField()
    crop_width = models.PositiveIntegerField()
    crop_height = models.PositiveIntegerField()
    width = models.PositiveIntegerField(editable=False)
    height = models.PositiveIntegerField(editable=False)

    objects = FormatedPhotoManager()

    @property
    def url(self):
        "Returns url of the photo file."
        return self.image.url

    def _generate_img(self):
        crop_box = None
        if self.crop_left:
            crop_box = (self.crop_left, self.crop_top, \
                    self.crop_left + self.crop_width, self.crop_top + self.crop_height)

        important_box = None
        if self.photo.important_top is not None:
            p = self.photo
            important_box = (p.important_left, p.important_top, p.important_right, p.important_bottom)

        formatter = Formatter(self.photo._get_image(), self.format, crop_box=crop_box, important_box=important_box)

        return formatter.format()

    def generate(self, save=True):
        "Generates photo file in current format"
        stretched_photo, crop_box = self._generate_img()

        # set crop_box to (0,0,0,0) if photo not cropped
        if not crop_box:
            crop_box = 0,0,0,0

        self.crop_left, self.crop_top, right, bottom = crop_box
        self.crop_width = right - self.crop_left
        self.crop_height = bottom - self.crop_top

        self.width, self.height = stretched_photo.size

        f = StringIO()
        stretched_photo.save(f, format=Image.EXTENSION[path.splitext(self.photo.image.name)[1]], quality=self.format.resample_quality)
        f.seek(0)

        self.image.save(self.file(), ContentFile(f.read()), save)

    def save(self, **kwargs):
        """Overrides models.Model.save

        - Removes old file from the FS
        - Generates new file.
        """
        self.remove_file()
        if not self.image:
            self.generate(save=False)
        else:
            self.image.name = self.file()
        super(FormatedPhoto, self).save(**kwargs)
        if redis:
            redis.hmset(
                REDIS_FORMATTED_PHOTO_KEY % (self.photo_id, self.format.id),
                {
                    'url': self.url,
                    'width': self.width,
                    'height': self.height,
                }
            )

    def delete(self):
        self.remove_file()
        if redis:
            redis.delete(REDIS_FORMATTED_PHOTO_KEY % (self.photo_id, self.format.id))
        super(FormatedPhoto, self).delete()

    def remove_file(self):
        if self.image.name:
            self.image.delete()

    def file(self):
        """ Method returns formated photo path - derived from format.id and source Photo filename """
        source_file = path.split(self.photo.image.name)
        return path.join(source_file[0],  str (self.format.id) + '-' + source_file[1])

    def __unicode__(self):
        return u"%s - %s" % (self.photo, self.format)

    class Meta:
        verbose_name = _('Formated photo')
        verbose_name_plural = _('Formated photos')
        unique_together = (('photo','format'),)

