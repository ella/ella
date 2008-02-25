import Image
from datetime import datetime
import shutil
from os import path
from fs import change_basename
from imageop import ImageStretch, detect_img_type
import shutil, os, glob

from django.db import models, transaction
from django.conf import settings
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site

from ella.core.models import Author, Source, Category, Listing
from ella.core.managers import RelatedManager
from ella.core.box import Box
from ella.utils.filemanipulation import file_rename

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

PHOTOS_TYPE_EXTENSION = {
    'JPEG': '.jpg',
    'PNG': '.png',
    'GIF': '.gif'
}

# from: http://code.djangoproject.com/wiki/CustomUploadAndFilters
def auto_rename(file_path, new_name, extension=None):
    """
    Renames a file, keeping the extension.

    Parameters:
    - file_path: the file path relative to MEDIA_ROOT
    - new_name: the new basename of the file (no extension)

    Returns the new file path on success or the original file_path on error.
    """
    if file_path == '':
        return ''
    suff = None
    if extension:
        suff = '.%s' % extension
    new_path = change_basename(file_path, new_name, suff)
    if new_path != file_path:
        try:
            shutil.move(os.path.join(settings.MEDIA_ROOT, file_path), os.path.join(settings.MEDIA_ROOT, new_path))
        except IOError:
            new_path = file_path
    return new_path


class PhotoBox(Box):
    def get_context(self):
        cont = super(PhotoBox, self).get_context()
        cont.update({
                'title' : self.params.get('title', self.obj.title),
                'alt' : self.params.get('alt', ''),
                'description' : self.params.get('description', self.obj.description),
                'show_title' : self.params.get('show_title', ''),
                'show_description' : self.params.get('show_description', ''),
                'show_authors' : self.params.get('show_authors', ''),
                'show_detail' : self.params.get('show_detail', ''),
})
        return cont

class Photo(models.Model):
    title = models.CharField(_('Title'), max_length=200)
    description = models.TextField(_('Description'), blank=True)
    slug = models.CharField(max_length=200, unique=True, db_index=True)
    image = models.ImageField(upload_to='photos/%Y/%m/%d', height_field='height', width_field='width') # save it to YYYY/MM/DD structure
    width = models.PositiveIntegerField(editable=False)
    height = models.PositiveIntegerField(editable=False)

    # Authors and Sources
    authors = models.ManyToManyField(Author, verbose_name=_('Authors') , related_name='photo_set')
    source = models.ForeignKey(Source, blank=True, null=True, verbose_name=_('Source'))

    created = models.DateTimeField(default=datetime.now, editable=False)

    def __unicode__(self):
        return self.title

    def thumb(self):
        """
        do thumbnails
        """
        from django.utils.safestring import mark_safe
        spl = path.split(self.image)
        woExtension = spl[1].rsplit('.', 1)[0]
        imageType = detect_img_type(settings.MEDIA_ROOT + self.image)
        if not imageType:
            return mark_safe("""<strong>%s</strong>""" % ugettext('Thumbnail not available'))
        ext = PHOTOS_TYPE_EXTENSION[ imageType ]
        filename = 'thumb-%s%s' % (woExtension, ext)
        tPath = (spl[0] , filename)
        tinythumb = path.join(*tPath)
        tinythumbPath = settings.MEDIA_ROOT + tinythumb
        if not path.exists(tinythumbPath):
            try:
                im = Image.open(settings.MEDIA_ROOT + self.image)
                im.thumbnail(PHOTOS_THUMB_DIMENSION , Image.ANTIALIAS)
                im.save(tinythumbPath, imageType)
            except IOError:
                # TODO Logging something wrong
                return mark_safe("""<strong>%s</strong>""" % ugettext('Thumbnail not available'))
        return mark_safe("""<a href="%s%s"><img src="%s%s" alt="Thumbnail %s" /></a>""" % (settings.MEDIA_URL, self.image, settings.MEDIA_URL, tinythumb, self.title))
    thumb.allow_tags = True

    def Box(self, box_type, nodelist):
        return PhotoBox(self, box_type, nodelist)

    @transaction.commit_on_success
    def save(self):
        # prefill the slug with the ID, it requires double save
        if not self.id:
            super(Photo, self).save()
            self.slug = str(self.id) + '-' + self.slug
        # rename image by slug
        imageType = detect_img_type(settings.MEDIA_ROOT + self.image)
        self.image = file_rename(self.image, self.slug, PHOTOS_TYPE_EXTENSION[ imageType ])
        super(Photo, self).save()

    def ratio(self):
        if self.height:
            return float(self.width) / self.height
        else:
            return None

    class Meta:
        verbose_name = _('Photo')
        verbose_name_plural = _('Photos')
        ordering = ('-created',)


class Format(models.Model):
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

    def __unicode__(self):
        return  u"%s (%sx%s) " % (self.name, self.max_width, self.max_height)

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
    def __unicode__(self):
        return u"%s - %s" % (self.filename, self.format)

    @property
    def url(self):
        from os import path
        if not path.exists(settings.MEDIA_ROOT):
            # NFS not available - we have no chance of creating it
            return self.format.get_blank_img()['url']

        if path.exists(settings.MEDIA_ROOT + self.filename):
            # image exists
            return settings.MEDIA_URL + self.filename

        # image does not exist - try and create it
        try:
            self.generate()
            return settings.MEDIA_URL + self.filename
        except (IOError, SystemError):
            return self.format.get_blank_img()['url']


    def generate(self):
        i = ImageStretch(filename=self.photo.get_image_filename(), formated_photo=self)
        stretched_photo = i.stretch_image()
        self.width, self.height = stretched_photo.size
        self.filename = self.file(relative=True)
        stretched_photo.save(self.file(), quality=self.format.resample_quality)


    def save(self):
        import os
        from os import path
        if path.exists(settings.MEDIA_ROOT + self.file(relative=True)):
            os.remove(settings.MEDIA_ROOT + self.file(relative=True))
        self.generate()
        super(FormatedPhoto, self).save()


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

from django import newforms as forms
class FormatedPhotoForm(forms.BaseForm):
    def clean(self):
        """
        Validation function that checks the dimensions of the crop whether it fits into the original and the format.
        """
        data = self.cleaned_data
        photo = data['photo']
        if (
            (data['crop_left'] >  photo.width) or
            (data['crop_top'] > photo.height) or
            ((data['crop_left'] + data['crop_width']) > photo.width) or
            ((data['crop_top'] + data['crop_height']) > photo.height)
):
            raise forms.ValidationError, ugettext("The specified crop coordinates do not fit into the source photo.")

        #my_ratio = float(data['crop_width']) / data['crop_height']
        #fmt = data['format']
        #if fmt.flexible_height:
        #    fmt_ratios = float(fmt.max_width) / fmt.flexible_max_height, float(fmt.max_width) / fmt.max_height
        #    if not(fmt_ratios[0] <= my_ratio <= fmt_ratios[1]):
        #        raise forms.ValidationError, ugettext('The specified crop ratio does not agree with the defined format.')
        #elif my_ratio - (float(fmt.max_width) / fmt.max_height) > 0.01:
        #    raise forms.ValidationError, ugettext('The specified crop ratio does not agree with the defined format.')

        return data



from django.contrib import admin

class FormatOptions(admin.ModelAdmin):
    list_display = ('name', 'max_width', 'max_height', 'stretch', 'resample_quality',)
    list_filter = ('site', 'stretch', 'nocrop',)
    search_fields = ('name',)


from tagging.models import TaggingInlineOptions

class CropAreaWidget(forms.TextInput):
    class Media:
        JS_JQUERY = 'js/jquery.js'
        JS_INTERFACE = 'js/interface.js'
        JS_CROP = 'js/crop.js'
        CSS_CROP = 'css/crop.css'
        js = (
            settings.ADMIN_MEDIA_PREFIX + JS_JQUERY,
            settings.ADMIN_MEDIA_PREFIX + JS_INTERFACE,
            settings.ADMIN_MEDIA_PREFIX + JS_CROP,
)
        css = {
            'screen': (settings.ADMIN_MEDIA_PREFIX + CSS_CROP,),
}

    def __init__(self, attrs={}):
        super(CropAreaWidget, self).__init__(attrs={'class': 'crop'})


class FormatedPhotoInlineOptions(admin.TabularInline):
    model = FormatedPhoto
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in ['crop_width', 'crop_height', 'crop_left', 'crop_top']:
            kwargs['widget'] = CropAreaWidget
        return super(self.__class__, self).formfield_for_dbfield(db_field, **kwargs)


class PhotoOptions(admin.ModelAdmin):
    inlines = (FormatedPhotoInlineOptions, TaggingInlineOptions,)
    list_display = ('title', 'width', 'height', 'thumb') ## 'authors')
    list_filter = ('created',)
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'image', 'description',)

    def __call__(self, request, url):
        if url and url.endswith('json'):
            from ella.photos.views import format_photo_json
            return format_photo_json(request, *url.split('/')[-3:-1])
        return super(PhotoOptions, self).__call__(request, url)


class FormatedPhotoOptions(admin.ModelAdmin):
    base_form = FormatedPhotoForm
    list_display = ('filename', 'format', 'width', 'height')
    list_filter = ('format',)
    search_fields = ('filename',)
    raw_id_fields = ('photo',)


admin.site.register(Format, FormatOptions)
admin.site.register(Photo, PhotoOptions)
admin.site.register(FormatedPhoto, FormatedPhotoOptions)

