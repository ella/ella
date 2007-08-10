from django.db import models
from django.conf import settings
import datetime, Image
import shutil
from os import path
from fs import change_basename
import shutil, os, glob
from ella.core.models import Author, Source, Category
from ella.core.box import Box

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
MEDIA_ROOT = settings.MEDIA_ROOT

# from: http://code.djangoproject.com/wiki/CustomUploadAndFilters
def auto_rename(file_path, new_name):
    """
    Renames a file, keeping the extension.

    Parameters:
    - file_path: the file path relative to MEDIA_ROOT
    - new_name: the new basename of the file (no extension)

    Returns the new file path on success or the original file_path on error.
    """
    # Return if no file given
    if file_path == '':
        return ''
    # Get the new name
    new_path = change_basename(file_path, new_name)

    # Changed?
    if new_path != file_path:
        # Try to rename
        try:
            shutil.move(os.path.join(settings.MEDIA_ROOT, file_path), os.path.join(settings.MEDIA_ROOT, new_path))
        except IOError:
            # Error? Restore original name
            new_path = file_path

    return new_path

class Photo(models.Model):

    def __unicode__(self):
        return u"%s" % (self.title)
    # do thumbnails
    def thumb(self):
        tinythumb = path.split(self.image) #.replace('\\','/').split('/')
        tinythumb = (tinythumb[0] , 'thumb-' + tinythumb[1])
        tinythumb = path.join(*tinythumb)
        if not path.exists(MEDIA_ROOT + tinythumb):
            try:
                im = Image.open(MEDIA_ROOT + self.image)
                im.thumbnail(PHOTOS_THUMB_DIMENSION , Image.ANTIALIAS)
                im.save(MEDIA_ROOT+tinythumb, "JPEG")
            except IOError:
                # TODO Logging something wrong
                return """<strong>%s</strong>""" % _('Thumbnail not available')
        return """<a href="/photo/%s"><img src="/thumb/%s" alt="Thumbnail %s" /></a>""" % (self.image, tinythumb, self.title)
    thumb.allow_tags = True

    # title is required
    # TODO FIXME how work with URLs a filenames

    title = models.CharField(_('Title'), maxlength=200)
    description = models.TextField(_('Description'), blank=True)
    slug = models.CharField(maxlength=200, unique=True)
    image = models.ImageField(upload_to='photos/%Y/%m/%d', height_field='height', width_field='width') # save it to YYYY/MM/DD structure
    width = models.PositiveIntegerField(editable=False)
    height = models.PositiveIntegerField(editable=False)

    def Box(self, box_type, nodelist):
        return Box(self, box_type, nodelist)

    # TODO zajistit unikatnost nazvu slugu
    def save(self):
        self.image = auto_rename(self.image, self.slug)
        super(Photo, self).save()

    def ratio(self):
        if self.height:
            return float(self.width) / self.height
        else:
            return None

    # Authors and Sources
    authors = models.ManyToManyField(Author, verbose_name=_('Authors') , related_name='photo_set')
    source = models.ForeignKey(Source, blank=True, null=True, verbose_name=_('Source'))
    category = models.ForeignKey(Category, verbose_name=_('Category'))

    class Meta:
        verbose_name = _('Photo')
        verbose_name_plural = _('Photos')
        ordering = ('-id',)

class Format(models.Model):
    def __unicode__(self):
        return  u"%s (%sx%s) " % (self.name, self.max_width, self.max_height)

    name = models.CharField(maxlength=80)
    max_width = models.PositiveIntegerField()
    max_height = models.PositiveIntegerField()
    stretch = models.BooleanField()
    resample_quality = models.IntegerField(choices=PHOTOS_FORMAT_QUALITY, default=85)
    def ratio(self):
        if self.max_height:
            return float(self.max_width) / self.max_height
        else:
            return None

    class Meta:
        verbose_name = _('Format')
        verbose_name_plural = _('Formats')
        ordering = ('name', '-max_width',)

class FormatedPhoto(models.Model):
    def __unicode__(self):
        return u"%s - %s" % (self.filename, self.format)

    photo = models.ForeignKey(Photo)
    format = models.ForeignKey(Format)
    filename = models.CharField(maxlength=300, editable=False) # derive local filename and url
    crop_left = models.PositiveIntegerField(default=0)
    crop_top = models.PositiveIntegerField(default=0)
    crop_width = models.PositiveIntegerField(default=0)
    crop_height = models.PositiveIntegerField(default=0)
    width = models.PositiveIntegerField(editable=False)
    height = models.PositiveIntegerField(editable=False)

    # FIXME TODO - error raises atp.
    # return crop
    def crop(self):
        """ Method return rectangle of crop """
        return (self.crop_left, self.crop_top, self.crop_left + self.crop_width, self.crop_top + self.crop_height)

    def set_crop_from_bbox(self, bbox):
        self.crop_left = bbox[0]
        self.crop_top = bbox[1]
        self.crop_width = bbox[2] - bbox[0]
        self.crop_height = bbox[3] - bbox[1]

    # repair crop to be inside original photo if not
    # and if crop is invalid (negative width or height) return False
    def crop_valid(self):
        # TODO: move this as validation to adminForm
        crop = self.crop()
        photo = self.photo
        self.crop_left = min(crop[0], photo.width)
        self.crop_top = min(crop[1], photo.height)
        self.crop_width = min(crop[2] - self.crop_left , photo.width - self.crop_left)
        self.crop_height = min(crop[3] - self.crop_top , photo.height - self.crop_top)
        crop = self.crop()
        return (crop[2]-crop[0] > 0) and (crop[3]-crop[1] > 0)

    def get_stretch_dimension(self):
        """ Method return stretch dimension of crop to fit inside max format rectangle """
        if self.format.ratio() < self.crop_ratio() :
            stretch_width = self.format.max_width
            stretch_height = min(self.format.max_height, int(stretch_width/self.crop_ratio())) # dimension must be integer
        else: #if(self.photo.ratio() < self.crop_ratio()):
            stretch_height = self.format.max_height
            stretch_width = min(self.format.max_width, int(stretch_height*self.crop_ratio()))
        return (stretch_width, stretch_height)

    def crop_is_inside_format(self):
        """ Check if crop rectangle is inside format maximal rectangle """
        return (self.crop_width < self.format.max_width) and (self.crop_height < self.format.max_height)

    def save(self):
        source_file = self.photo.get_image_filename()
        source = Image.open(source_file)
        source_bbox = source.getbbox()
        # if valid crop do
        if self.crop_valid():
            bbox = self.crop()
        # else stay original
        else:
            bbox = source_bbox
            self.set_crop_from_bbox(bbox)
        # generate crop
        cropped_photo = source.crop(bbox)
        # if format stretches everything (bigger & smaller crops)
        if self.format.stretch:
            stretched_photo = cropped_photo.resize(self.get_stretch_dimension(), Image.BICUBIC)
        # if is crop smaller than format & stretch only bigger crops
        elif self.crop_is_inside_format() :
            stretched_photo = cropped_photo
        # others
        else:
            stretched_photo = cropped_photo.resize(self.get_stretch_dimension())

        photo_bbox = stretched_photo.getbbox()
        self.width, self.height = photo_bbox[2], photo_bbox[3]
        self.filename = self.file(relative=True)
        stretched_photo.save(self.file(), quality=self.format.resample_quality)
        super (FormatedPhoto, self).save()
    # return crop_ratio

    def crop_ratio(self):
        if(self.crop_height) :
            return float(self.crop_width) / self.crop_height
        else:
            return None

    # FIXME - formated photo is the same type as source photo eq. png => png, jpg => jpg
    def file(self, relative=False):
        """ Method returns formated photo path - derived from format.id and source Photo filename """
        if relative:
            source_file = path.split(self.photo.image)
        else:
            source_file = path.split(self.photo.get_image_filename())
        return path.join(source_file[0],  str (self.format.id) + '-' + source_file[1])

    class Meta:
        verbose_name = _('Formated photo')
        verbose_name_plural = _('Formated photos')
        unique_together = (('photo','format'),)
        ordering = ('-id',)
#   generator

from django.contrib import admin

class FormatOptions(admin.ModelAdmin):
    list_display = ('name', 'max_width', 'max_height', 'stretch', 'resample_quality')

from django import newforms as forms
class PhotoForm(forms.BaseForm):
    pass

class FormatedPhotoForm(forms.BaseForm):
#    def __init__(self, *args, **kwargs):
#        super(FormatedPhotoForm, self).__init__(*args, **kwargs)
#        if hasattr(self, 'instance'):
#            self.fields['photo'].required = False

    # FIXME XXX
    def clean(self):
        data = self.cleaned_data
#        if 'crop_width' not in data or 'crop_width' not in data or 'crop_left' not in data or 'crop_top' not in data:
#            data['crop_left'], data['crop_top'], data['crop_width'], data['crop_height'] = 0, 0, 100, 100
#        if 'crop_width' in data and 'crop_height' in data and data['crop_width'] == None and data['crop_height'] == None:
#        raise forms.ValidationError, _("Vole, mas to blbe")
        return data

class PhotoOptions(admin.ModelAdmin):
    base_form = PhotoForm
    list_display = ('title', 'image', 'width', 'height', 'thumb') ## 'authors')
    prepopulated_fields = {'slug': ('title',)}

class FormatedPhotoOptions(admin.ModelAdmin):
    base_form = FormatedPhotoForm
    list_display = ('filename', 'format', 'width', 'height')
    list_filter = ('format',)
    search_fields = ('filename',)
    raw_id_fields = ('photo',)

#if  __name__ != '__main__':
admin.site.register(Format, FormatOptions)
admin.site.register(Photo, PhotoOptions)
admin.site.register(FormatedPhoto, FormatedPhotoOptions)

# Create your models here.
