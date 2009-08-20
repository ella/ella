from os import path, makedirs

import Image

from django import forms
from django.conf import settings
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from ella import newman
from ella.media.models import Media, Section, Usage
from ella.photos.models import Photo
from ella.core.newman_admin import PublishableAdmin

from ella.newman.widgets import ForeignKeyRawIdWidget

class MediaPhotoWidget(ForeignKeyRawIdWidget):
    """
    Widget for photo with option to generate screenshot from video

    TODO: more user friendly form
    """
    def render(self, name, value, attrs=None):
        return mark_safe(
             'Generate photo <input type="checkbox" name="%s" %s /> at <input type="text" name="%s" /> second or use custom: %s' % \
             (name + '_auto',
              value and ' ' or 'checked="true"',
              name + '_time',
              super(MediaPhotoWidget, self).render(name, value, attrs),))



class MediaForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(MediaForm, self).__init__(*args, **kwargs)
        # Use PhotoWidget for photo field
        self.fields['photo'].widget =  MediaPhotoWidget(Media._meta.get_field_by_name('photo')[0].rel)


def get_img_size(filename):
    im = Image.open(filename)
    return {
        'width': im.size[0],
        'height': im.size[1]
    }

class SectionInline(newman.NewmanTabularInline):
    model = Section
    extra = 5

class UsageInline(newman.NewmanTabularInline):
    model = Usage



class MediaAdmin(PublishableAdmin):

    def __init__(self, *args, **kwargs):
        super(MediaAdmin, self).__init__(*args, **kwargs)
        self.form = MediaForm

    inlines = [SectionInline, UsageInline]

    rich_text_fields = {'small': ('description',), None: ('text',)}

    fieldsets = (
        (_("Heading"), {'fields': ('title', 'file',)}),
        (_("Updated, slug"), {'fields': ('updated', 'slug',), 'classes': ('collapsed',)}),
        (_("Metadata"), {'fields': ('photo', 'category', 'authors', 'source')}),
        (_("Content"), {'fields': ('description', 'text',)}),
    )

    def save_model(self, request, obj, form, change):

        if form.data.has_key('photo_auto'):
            time = None
            if form.data.has_key('photo_time') and form.data['photo_time']:
                time = int(form.data['photo_time'])
            self.generate_photo(obj, time)

        super(MediaAdmin, self).save_model(request, obj, form, change)

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



newman.site.register(Media, MediaAdmin)

