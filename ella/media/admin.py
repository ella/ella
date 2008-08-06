from os import path, makedirs

from django.contrib import admin

from ella.media.models import Media, Section


from ella.core.admin import PlacementInlineOptions
from ella.photos.models import Photo
from ella.photos.imageop import get_img_size
from ella.tagging.admin import TaggingInlineOptions

from django.conf import settings
from django.forms import ModelForm
from django.template.defaultfilters import slugify

class MediaForm(ModelForm):

    def save(self, commit=True):

        instance = super(MediaForm, self).save(False)
        if (instance.photo is None):
            dir_name = Photo._meta.get_field_by_name('image')[0].get_directory_name()
            file_name = path.join(dir_name, 'screenshot-' + instance.file.token)
            try:
                makedirs(path.join(settings.MEDIA_ROOT, dir_name))
            except OSError:
                # Directory already exists
                pass
            instance.file.create_thumb(path.join(settings.MEDIA_ROOT, file_name))
            photo = Photo()
            photo.title = "%s screenshot" % instance.title
            photo.slug = slugify(photo.title)
            photo.image = file_name
            size = get_img_size(path.join(settings.MEDIA_ROOT, file_name))
            photo.width = size['width']
            photo.height = size['height']
            photo.save()
            instance.photo = photo
        if commit:
            instance.save()

        return instance

class SectionInline(admin.TabularInline):
    model = Section

class MediaOptions(admin.ModelAdmin):

    def __init__(self, *args, **kwargs):
        super(MediaOptions, self).__init__(*args, **kwargs)
        self.form = MediaForm

    prepopulated_fields = {'slug' : ('title',)}

    list_display = ('title',)
    list_filter = ('created', 'updated',)
    search_fields = ('title', 'slug', 'description', 'content',)

    raw_id_fields = ('photo',)

    inlines = (PlacementInlineOptions, TaggingInlineOptions, SectionInline)

#    rich_text_fields = {None: ('description', 'content',)}


admin.site.register(Media, MediaOptions)
