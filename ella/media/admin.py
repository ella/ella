from os import path, makedirs

import Image

from django.conf import settings
from django.contrib import admin
from django.template.defaultfilters import slugify

from ella.ellaadmin.options import EllaAdminOptionsMixin, EllaModelAdmin
from ella.media.models import Media, Section, Usage
from ella.media.forms import MediaForm
from ella.photos.models import Photo


def get_img_size(filename):
    im = Image.open(filename)
    return {
        'width': im.size[0], 
        'height': im.size[1]
    }

class SectionInline(admin.TabularInline):
    model = Section
    extra = 5

class UsageInline(admin.TabularInline):
    model = Usage

class MediaOptions(EllaAdminOptionsMixin, EllaModelAdmin):

    def __init__(self, *args, **kwargs):
        super(MediaOptions, self).__init__(*args, **kwargs)
        self.form = MediaForm

    prepopulated_fields = {'slug' : ('title',)}

    list_display = ('title',)
    list_filter = ('created', 'updated',)
    search_fields = ('title', 'slug', 'description', 'text',)

    inlines = (SectionInline, UsageInline)

    rich_text_fields = {None: ('description', 'text',)}

    def save_model(self, request, obj, form, change):

        if form.data.has_key('photo_auto'):
            time = None
            if form.data.has_key('photo_time') and form.data['photo_time']:
                time = int(form.data['photo_time'])
            self.generate_photo(obj, time)

        super(MediaOptions, self).save_model(request, obj, form, change)

        from nc.cdnclient.forms import TargetsForm
        form = TargetsForm(obj.file, data=form.data, prefix='file')
        form.create_formats()

    def generate_photo(self, instance, time):
        # TODO: handle fails
        dir_name = Photo._meta.get_field_by_name('image')[0].get_directory_name()
        file_name = path.join(dir_name, 'screenshot-' + instance.file.token)
        try:
            makedirs(path.join(settings.MEDIA_ROOT, dir_name))
        except OSError:
            # Directory already exists
            pass
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



admin.site.register(Media, MediaOptions)

