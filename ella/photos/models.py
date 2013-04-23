import logging
from PIL import Image
from os import path
from cStringIO import StringIO
import os.path
import string

from django.db import models
from django.db.models import signals
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_unicode, smart_str
from django.contrib.sites.models import Site
from django.core.files.base import ContentFile
from django.conf import settings
from django.template.defaultfilters import slugify

from app_data import AppDataField

from ella.core.models.main import Author, Source
from ella.core.cache.utils import get_cached_object
from ella.photos.conf import photos_settings
from ella.utils.timezone import now

from formatter import Formatter

__all__ = ("Format", "FormatedPhoto", "Photo")

log = logging.getLogger('ella.photos')

redis = None
REDIS_PHOTO_KEY = 'photo:%s'
REDIS_FORMATTED_PHOTO_KEY = 'photo:%s:%s'

if hasattr(settings, 'PHOTOS_REDIS'):
    try:
        from redis import Redis
    except:
        log.error('Redis support requested but Redis client not installed.')
        redis = None
    else:
        redis = Redis(**getattr(settings, 'PHOTOS_REDIS'))


def upload_to(instance, filename):
    name, ext = os.path.splitext(filename)
    if instance.slug:
        name = instance.slug
    ext = photos_settings.TYPE_EXTENSION.get(instance._get_image().format, ext.lower())
    instance.image.file.seek(0)

    return os.path.join(
        force_unicode(now().strftime(smart_str(photos_settings.UPLOAD_TO))),
        name + ext
    )


class Photo(models.Model):
    """
    Represents original (unformated) photo uploaded by user. Used as source
    object for all the formatting stuff and to keep the metadata common to
    all related ``FormatedPhoto`` objects.
    """
    title = models.CharField(_('Title'), max_length=200)
    description = models.TextField(_('Description'), blank=True)
    slug = models.SlugField(_('Slug'), max_length=255)
    # save it to YYYY/MM/DD structure
    image = models.ImageField(_('Image'), upload_to=upload_to,
        max_length=255, height_field='height', width_field='width')
    width = models.PositiveIntegerField(editable=False)
    height = models.PositiveIntegerField(editable=False)

    # important area
    important_top = models.PositiveIntegerField(null=True, blank=True)
    important_left = models.PositiveIntegerField(null=True, blank=True)
    important_bottom = models.PositiveIntegerField(null=True, blank=True)
    important_right = models.PositiveIntegerField(null=True, blank=True)

    # Authors and Sources
    authors = models.ManyToManyField(Author, verbose_name=_('Authors'), related_name='photo_set')
    source = models.ForeignKey(Source, blank=True, null=True, verbose_name=_('Source'), on_delete=models.SET_NULL)

    created = models.DateTimeField(auto_now_add=True)

    # generic JSON field to store app cpecific data
    app_data = AppDataField()

    class Meta:
        verbose_name = _('Photo')
        verbose_name_plural = _('Photos')

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return self.image.url

    def get_image_info(self):
        return {
            'url': self.image.url,
            'width': self.width,
            'height': self.height,
        }

    def _get_image(self):
        if not hasattr(self, '_pil_image'):
            self.image.open()
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
            try:
                old = Photo.objects.get(pk=self.pk)

                force_update = True
                # delete formatedphotos if new image was uploaded
                if old.image != self.image:
                    for f_photo in self.formatedphoto_set.all():
                        f_photo.delete()
            except Photo.DoesNotExist:
                # somebody is just trying to create new model with given PK
                force_update = False

            super(Photo, self).save(force_update=force_update)

    def ratio(self):
        "Return photo's width to height ratio"
        if self.height:
            return float(self.width) / self.height
        else:
            return None

    def get_formated_photo(self, format):
        "Return formated photo"
        return FormatedPhoto.objects.get_photo_in_format(self, format)


FORMAT_CACHE = {}


class FormatManager(models.Manager):
    def get_for_name(self, name):
        try:
            return FORMAT_CACHE[name]
        except KeyError:
            FORMAT_CACHE[name] = format = get_cached_object(Format, name=name, sites__id=settings.SITE_ID)
        return format


class Format(models.Model):
    """
    Defines per-site photo sizes together with rules how to adhere to them.

    This includes:

    * maximum width and height
    * cropping settings
    * stretch (rescale) settings
    * sample quality
    """
    name = models.CharField(_('Name'), max_length=80)
    max_width = models.PositiveIntegerField(_('Max width'))
    max_height = models.PositiveIntegerField(_('Max height'))
    flexible_height = models.BooleanField(_('Flexible height'), help_text=_((
        'Determines whether max_height is an absolute maximum, or the formatted'
        'photo can vary from max_height to flexible_max_height.')))
    flexible_max_height = models.PositiveIntegerField(_('Flexible max height'),
        blank=True, null=True)
    stretch = models.BooleanField(_('Stretch'))
    nocrop = models.BooleanField(_('Do not crop'))
    resample_quality = models.IntegerField(_('Resample quality'),
        choices=photos_settings.FORMAT_QUALITY, default=85)
    sites = models.ManyToManyField(Site, verbose_name=_('Sites'))
    master = models.ForeignKey('self', verbose_name=_('Master'), null=True, blank=True, help_text=_((
        'When generating formatted image, use the image formatted to master format instead of the original.'
        'Useful when editors crop certain formats by hand and you wish to re-use those coordinates automatically.'
    )))

    objects = FormatManager()

    class Meta:
        verbose_name = _('Format')
        verbose_name_plural = _('Formats')

    def __unicode__(self):
        return  u"%s (%sx%s) " % (self.name, self.max_width, self.max_height)

    def get_blank_img(self):
        """
        Return fake ``FormatedPhoto`` object to be used in templates when an error
        occurs in image generation.
        """
        if photos_settings.DEBUG:
            return self.get_placeholder_img()

        out = {
            'blank': True,
            'width': self.max_width,
            'height': self.max_height,
            'url': photos_settings.EMPTY_IMAGE_SITE_PREFIX + 'img/empty/%s.png' % (self.name),
        }
        return out

    def get_placeholder_img(self):
        """
        Returns fake ``FormatedPhoto`` object grabbed from image placeholder
        generator service for the purpose of debugging when images
        are not available but we still want to see something.
        """
        pars = {
            'width': self.max_width,
            'height': self.max_height
        }
        out = {
            'placeholder': True,
            'width': self.max_width,
            'height': self.max_height,
            'url': photos_settings.DEBUG_PLACEHOLDER_PROVIDER_TEMPLATE % pars
        }
        return out

    def ratio(self):
        """Return photo's width to height ratio"""
        return float(self.max_width) / self.max_height

    def save(self, **kwargs):
        """Overrides models.Model.save.

        - Delete formatted photos if format save and not now created
          (because of possible changes)
        """

        if self.id:
            for f_photo in self.formatedphoto_set.all():
                f_photo.delete()

        super(Format, self).save(**kwargs)


class FormatedPhotoManager(models.Manager):
    def get_photo_in_format(self, photo, format, include_original=True):
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
                if include_original:
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
                # use get or create because there is a possible race condition here
                # we don't want to JUST use get_or_create to go through cache 99.9% of the time
                formated_photo, _ = self.get_or_create(photo=photo, format=format)
            except (IOError, SystemError), e:
                log.warning("Cannot create formatted photo due to %s.", e)
                return format.get_blank_img()

        info = {
            'url': formated_photo.url,
            'width': formated_photo.width,
            'height': formated_photo.height,
        }
        if include_original:
            info['original'] = photo.get_image_info()

        return info


class FormatedPhoto(models.Model):
    """
    Cache-like container of specific photo of specific format. Besides
    the path to the generated image file, crop used is also stored together
    with new ``width`` and ``height`` attributes.
    """
    photo = models.ForeignKey(Photo)
    format = models.ForeignKey(Format)
    # save it to YYYY/MM/DD structure
    image = models.ImageField(upload_to=photos_settings.UPLOAD_TO,
        height_field='height', width_field='width', max_length=300)
    crop_left = models.IntegerField()
    crop_top = models.IntegerField()
    crop_width = models.IntegerField()
    crop_height = models.IntegerField()
    width = models.PositiveIntegerField(editable=False)
    height = models.PositiveIntegerField(editable=False)

    objects = FormatedPhotoManager()

    class Meta:
        verbose_name = _('Formated photo')
        verbose_name_plural = _('Formated photos')
        unique_together = (('photo', 'format'),)

    def __unicode__(self):
        return u"%s - %s" % (self.photo, self.format)

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

        image = None
        if crop_box is None and self.format.master_id:
            try:
                fp = FormatedPhoto.objects.get(format=self.format.master_id, photo=self.photo)
                image = Image.open(fp.image)
            except FormatedPhoto.DoesNotExist:
                pass

        if image is None:
            image = self.photo._get_image()
        formatter = Formatter(image, self.format, crop_box=crop_box, important_box=important_box)

        return formatter.format()

    def generate(self, save=True):
        """
        Generates photo file in current format.

        If ``save`` is ``True``, file is saved too.
        """
        stretched_photo, crop_box = self._generate_img()

        # set crop_box to (0,0,0,0) if photo not cropped
        if not crop_box:
            crop_box = 0, 0, 0, 0

        self.crop_left, self.crop_top, right, bottom = crop_box
        self.crop_width = right - self.crop_left
        self.crop_height = bottom - self.crop_top

        self.width, self.height = stretched_photo.size

        f = StringIO()
        imgf = (self.photo._get_image().format or
                Image.EXTENSION[path.splitext(self.photo.image.name)[1]])

        stretched_photo.save(f, format=imgf, quality=self.format.resample_quality)
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

    def delete(self):
        try:
            self.remove_file()
        except:
            log.warning('Error deleting FormatedPhoto %d-%s (%s).', self.photo_id, self.format.name, self.image.name)

        super(FormatedPhoto, self).delete()

    def remove_file(self):
        if self.image.name:
            self.image.delete()

    def file(self):
        """ Method returns formated photo path - derived from format.id and source Photo filename """
        if photos_settings.FORMATED_PHOTO_FILENAME is not None:
            return photos_settings.FORMATED_PHOTO_FILENAME(self)
        source_file = path.split(self.photo.image.name)
        return path.join(source_file[0], str(self.format.id) + '-' + source_file[1])

if redis:
    def store_photo(instance, **kwargs):
        if instance.image:
            redis.hmset(REDIS_PHOTO_KEY % instance.pk, instance.get_image_info())

    def remove_photo(instance, **kwargs):
        redis.delete(REDIS_PHOTO_KEY % instance.id)

    def store_formated_photo(instance, **kwargs):
        redis.hmset(
            REDIS_FORMATTED_PHOTO_KEY % (instance.photo_id, instance.format.id),
            {
                'url': instance.url,
                'width': instance.width,
                'height': instance.height,
            }
        )

    def remove_formated_photo(instance, **kwargs):
        redis.delete(REDIS_FORMATTED_PHOTO_KEY % (instance.photo_id, instance.format.id))

    signals.post_save.connect(store_photo, sender=Photo)
    signals.post_delete.connect(remove_photo, sender=Photo)
    signals.post_save.connect(store_formated_photo, sender=FormatedPhoto)
    signals.post_delete.connect(remove_formated_photo, sender=FormatedPhoto)
