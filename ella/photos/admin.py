from django import forms
from django.contrib import admin
from django.conf import settings
from django.utils.translation import ugettext
from django.forms.util import ValidationError
from django.utils.translation import ugettext_lazy as _

from ella.ellaadmin.options import EllaAdminOptionsMixin, EllaModelAdmin

from ella.photos.models import FormatedPhoto, Format, Photo
from ella.photos.views import format_photo_json, thumb_url
from ella.photos.conf import photos_settings

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
            # raise forms.ValidationError, ugettext("The specified crop coordinates do not fit into the source photo.")
            raise ValidationError, ugettext("The specified crop coordinates do not fit into the source photo.")
        return data


class FormatOptions(admin.ModelAdmin):
    list_display = ('name', 'max_width', 'max_height', 'stretch', 'resample_quality',)
    list_filter = ('sites', 'stretch', 'nocrop',)
    search_fields = ('name',)


class CropAreaWidget(forms.TextInput):
    class Media:
        JS_INTERFACE = 'js/interface.js'
        JS_CROP = 'js/crop.js'
        CSS_CROP = 'css/crop.css'
        js = (
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
        return super(FormatedPhotoInlineOptions, self).formfield_for_dbfield(db_field, **kwargs)


class PhotoOptions(EllaAdminOptionsMixin, EllaModelAdmin):
    inlines = [ FormatedPhotoInlineOptions ]
    list_display = ('title', 'width', 'height', 'thumb', 'pk',) ## 'authors')
    list_filter = ('created',)
    search_fields = ('title', 'image', 'description', 'id',) # FIXME: 'tags__tag__name',)
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
            return format_photo_json(request, *url.split('/')[-3:-1])
        if url and url.endswith('thumburl'):
            return thumb_url(request, *url.split('/')[-3:-1])
        return super(PhotoOptions, self).__call__(request, url)


class FormatedPhotoOptions(EllaAdminOptionsMixin, admin.ModelAdmin):
    base_form = FormatedPhotoForm
    list_display = ('image', 'format', 'width', 'height')
    list_filter = ('format',)
    search_fields = ('image',)
    raw_id_fields = ('photo',)


admin.site.register(Format, FormatOptions)
admin.site.register(Photo, PhotoOptions)
admin.site.register(FormatedPhoto, FormatedPhotoOptions)

