from django import forms
from django.contrib import admin
from django.conf import settings
from django.utils.translation import ugettext
from django.forms.util import ValidationError
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.http import HttpResponse

from ella.photos.models import FormatedPhoto, Format, Photo
from ella.core.cache.utils import get_cached_object


class FormatedPhotoForm(forms.BaseForm):
    def clean(self):
        """
        Validation function that checks the dimensions of the crop whether it fits into the original and the format.
        """
        data = self.cleaned_data
        photo = data['photo']
        if (
            (data['crop_left'] > photo.width) or
            (data['crop_top'] > photo.height) or
            ((data['crop_left'] + data['crop_width']) > photo.width) or
            ((data['crop_top'] + data['crop_height']) > photo.height)
        ):
            # raise forms.ValidationError, ugettext("The specified crop coordinates do not fit into the source photo.")
            raise ValidationError(ugettext("The specified crop coordinates do not fit into the source photo."))
        return data


class FormatForm(forms.ModelForm):
    class Meta:
        model = Format

    def clean(self):
        """
        Check format name uniqueness for sites

        :return: cleaned_data
        """

        data = self.cleaned_data
        formats = Format.objects.filter(name=data['name'])
        if self.instance:
            formats = formats.exclude(pk=self.instance.pk)

        exists_sites = []
        for f in formats:
            for s in f.sites.all():
                if s in data['sites']:
                    exists_sites.append(s.__unicode__())

        if len(exists_sites):
            raise ValidationError(ugettext("Format with this name exists for site(s): %s" % ", ".join(exists_sites)))

        return data


class FormatOptions(admin.ModelAdmin):
    form = FormatForm
    list_display = ('name', 'max_width', 'max_height', 'stretch', 'resample_quality',)
    list_filter = ('sites', 'stretch', 'nocrop',)
    search_fields = ('name',)


class FormatedPhotoInlineOptions(admin.TabularInline):
    model = FormatedPhoto


class PhotoOptions(admin.ModelAdmin):
    @property
    def thumb_format(self):
        if not hasattr(self, '_thumb_format'):
            if not hasattr(settings, 'PHOTOS_THUMB_FORMAT'):
                self._thumb_format = None
            else:
                self._thumb_format = get_cached_object(Format, id=settings.PHOTOS_THUMB_FORMAT)

        return self._thumb_format

    def thumb(self, photo):
        if not self.thumb_format:
            return ''

        thumb_info = FormatedPhoto.objects.get_photo_in_format(photo, self.thumb_format)

        return mark_safe("""
            <a href="%s" title="%s" target="_blank">
                <img src="%s" alt="Thumbnail %s" />
            </a>""" % (photo.image.url, photo.title, thumb_info['url'], photo.title))
    thumb.allow_tags = True

    inlines = [FormatedPhotoInlineOptions]
    list_display = ('title', 'width', 'height', 'thumb', )
    list_filter = ('created',)
    search_fields = ('title', 'image', 'description', 'id',)
    suggest_fields = {'authors': ('name', 'slug',), 'source': ('name', 'url',)}
    rich_text_fields = {'small': ('description',)}
    ordering = ('-id',)

    fieldsets = (
        (_("Photo core"), {'fields': ('title', 'image', 'authors')}),
        (_("Photo extra"), {'fields': ('description', 'source')}),
        (_("Metadata"), {'fields': (('important_top', 'important_left', 'important_bottom', 'important_right'),)}),
    )

    def __call__(self, request, url):
        if url and url.endswith('json'):
            return self.format_photo_json(request, *url.split('/')[-3:-1])
        return super(PhotoOptions, self).__call__(request, url)

    def format_photo_json(self, request, photo, format):
        "Used in admin image 'crop tool'."
        try:
            photo = get_cached_object(Photo, pk=photo)
            format = get_cached_object(Format, pk=format)
            content = {
                'error': False,
                'image':settings.MEDIA_URL + photo.image,
                'width':photo.width,
                'height': photo.height,
                'format_width':format.max_width,
                'format_height':format.max_height
            }
        except (Photo.DoesNotExist, Format.DoesNotExist):
            content = {'error':True}
        return HttpResponse(simplejson.dumps(content))


class FormatedPhotoOptions(admin.ModelAdmin):
    base_form = FormatedPhotoForm
    list_display = ('image', 'format', 'width', 'height')
    list_filter = ('format',)
    search_fields = ('image',)
    raw_id_fields = ('photo',)


admin.site.register(Format, FormatOptions)
admin.site.register(Photo, PhotoOptions)
admin.site.register(FormatedPhoto, FormatedPhotoOptions)

