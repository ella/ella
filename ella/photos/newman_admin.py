from django import forms
from django.conf import settings
from django.utils.translation import ugettext
from django.forms.util import ValidationError

from ella import newman
from ella.tagging.admin import TaggingInlineOptions

from ella.photos.models import FormatedPhoto, Format, Photo
from ella.photos.views import format_photo_json, thumb_url

class FormatOptions(newman.NewmanModelAdmin):
    list_display = ('name', 'max_width', 'max_height', 'stretch', 'resample_quality',)
    list_filter = ('sites', 'stretch', 'nocrop', 'flexible_height',)
    search_fields = ('name',)

class FormatedPhotoInlineOptions(newman.NewmanTabularInline):
    model = FormatedPhoto

class PhotoOptions(newman.NewmanModelAdmin):
    inlines = []
    if 'ella.tagging' in settings.INSTALLED_APPS:
        inlines.append(TaggingInlineOptions)
    list_display = ('title', 'width', 'height', 'thumb', 'pk',)
    list_filter = ('created',)
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'image', 'description', 'id',)
    suggest_fields = {'authors': ('name', 'slug',), 'source': ('name', 'url',)}

    def __call__(self, request, url):
        if url and url.endswith('json'):
            return format_photo_json(request, *url.split('/')[-3:-1])
        if url and url.endswith('thumburl'):
            return thumb_url(request, *url.split('/')[-3:-1])
        return super(PhotoOptions, self).__call__(request, url)


class FormatedPhotoOptions(newman.NewmanModelAdmin):
    list_display = ('filename', 'format', 'width', 'height')
    list_filter = ('format',)
    search_fields = ('filename',)
    raw_id_fields = ('photo',)


newman.site.register(Format, FormatOptions)
newman.site.register(Photo, PhotoOptions)
newman.site.register(FormatedPhoto, FormatedPhotoOptions)

