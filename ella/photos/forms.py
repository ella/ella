'''
Created on 19.9.2011

@author: xaralis
'''
from django import forms
from django.utils.translation import ugettext_lazy as _

from ella.photos.models import Photo
from ella.newman.conf import newman_settings
from ella.newman.fields import RGBImageField

# Flash image uploader / editor
CSS_UPLOADIFY_LIB = 'css/uploadify.css'
JS_SWFOBJECT = 'js/swfobject.js'
JS_UPLOADIFY_LIB = 'js/jquery.uploadify.min.js' 
SWF_FLASH_UPLOADER = 'swf/uploadify.swf'

class MassUploadForm(forms.ModelForm):
    image_file = forms.ImageField(label=_('Image files'))
     
    class Media:
        js = (
            newman_settings.MEDIA_PREFIX + JS_SWFOBJECT,
            newman_settings.MEDIA_PREFIX + JS_UPLOADIFY_LIB,
            newman_settings.MEDIA_PREFIX + SWF_FLASH_UPLOADER,
        )
        css = {
            'screen': (newman_settings.MEDIA_PREFIX + CSS_UPLOADIFY_LIB,),
        }
    
    class Meta:
        model = Photo
        exclude = ('image', 'important_top', 'important_left', 'important_bottom',
            'important_right')
        
