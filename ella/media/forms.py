from django.contrib.admin import widgets
from django import forms
#from django.template import mark_safe
from django.utils.safestring import mark_safe

from ella.media.models import Media


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
