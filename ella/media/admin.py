from os import path, makedirs

from django.contrib import admin

from ella.media.models import Media, Section

#from ella.core.admin import PlacementInlineOptions
from ella.photos.models import Photo
from ella.photos.imageop import get_img_size
#from ella.tagging.admin import TaggingInlineOptions
from ella.ellaadmin.options import EllaAdminOptionsMixin

from django.conf import settings
from django.contrib.admin import widgets
from django.forms import ModelForm
from django.template.defaultfilters import slugify


class PhotoWidget(widgets.ForeignKeyRawIdWidget):
    """
    Widget for photo with option generate screenshit from video
    """
    def render(self, name, value, attrs=None):
        print value
        return 'Generate photo <input type="checkbox" name="%s" %s /> at <input type="text" name="%s" /> second or use custom: %s' % \
             (name + '_auto',
              value and ' ' or 'checked="true"',
              name + '_time',
              super(PhotoWidget, self).render(name, value, attrs),)

class MediaForm(ModelForm):

    def save(self, commit=True):
        instance = super(MediaForm, self).save(False)
        if (commit and self.data.has_key('photo_auto')):
            dir_name = Photo._meta.get_field_by_name('image')[0].get_directory_name()
            file_name = path.join(dir_name, 'screenshot-' + instance.file.token)
            try:
                makedirs(path.join(settings.MEDIA_ROOT, dir_name))
            except OSError:
                # Directory already exists
                pass
            time = None
            if self.data.has_key('photo_time') and self.data['photo_time']:
                time = int(self.data['photo_time'])
            instance.file.create_thumb(path.join(settings.MEDIA_ROOT, file_name), time=time)
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

class MediaOptions(EllaAdminOptionsMixin, admin.ModelAdmin):

    def __init__(self, *args, **kwargs):
        super(MediaOptions, self).__init__(*args, **kwargs)
        self.form = MediaForm

    def formfield_for_dbfield(self, db_field, **kwargs):
        if (db_field.name == 'photo'):
            kwargs['widget'] = PhotoWidget(db_field.rel)
        return super(MediaOptions, self).formfield_for_dbfield(db_field, **kwargs)

    prepopulated_fields = {'slug' : ('title',)}

    list_display = ('title',)
    list_filter = ('created', 'updated',)
    search_fields = ('title', 'slug', 'description', 'content',)

#    inlines = (PlacementInlineOptions, TaggingInlineOptions, SectionInline)
    inlines = (SectionInline,)

    rich_text_fields = {None: ('description', 'text',)}


admin.site.register(Media, MediaOptions)

