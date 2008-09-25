from os import path, makedirs

from django.conf import settings
from django.contrib.admin import widgets
from django import forms
from django.template.defaultfilters import slugify
from django.template import mark_safe

from ella.photos.models import Photo
from ella.media.models import Media
from ella.photos.imageop import get_img_size


class PhotoWidget(widgets.ForeignKeyRawIdWidget):
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
              super(PhotoWidget, self).render(name, value, attrs),))



class MediaForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(MediaForm, self).__init__(*args, **kwargs)
        # Use PhotoWidget for photo field
        self.fields['photo'].widget =  PhotoWidget(Media._meta.get_field_by_name('photo')[0].rel)


    def generate_photo(self, instance):
        # TODO: handle fails
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

    def save(self, commit=True):
        instance = super(MediaForm, self).save(False)
        if (commit and self.data.has_key('photo_auto')):
            self.generate_photo(instance)
        if commit:
            instance.save()
            from nc.cdnclient.forms import TargetsForm
            form = TargetsForm(instance.file, data=self.data, prefix='file')
            form.create_formats()

        return instance
