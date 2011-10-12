'''
Created on 19.9.2011

@author: xaralis
'''
from django import forms
from django.utils.translation import ugettext_lazy as _

from ella.photos.models import Photo
from ella.newman.conf import newman_settings

# Flash image uploader / editor
CSS_UPLOADIFY_LIB = 'css/uploadify.css'
JS_SWFOBJECT = 'js/swfobject.js'
JS_UPLOADIFY_LIB = 'js/jquery.uploadify.min.js' 
SWF_FLASH_UPLOADER = 'swf/uploadify.swf'

class MassUploadForm(forms.ModelForm):
#    authors = forms.CharField()
    
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
        fieldsets = (
            (_("Heading"), {'fields': ('title', 'slug')}),
            (_("Description"), {'fields': ('description',)}),
            (_("Metadata"), {'fields': ('authors', 'source', 'image')}),
        )
        exclude = ('important_top', 'important_left', 'important_bottom',
            'important_right')
        

#    def save(self, *args, **kwargs):
#        from ella.core.models import Author
#        self.instance.authors = Author.objects.filter(
#            pk__in=self.cleaned_data['authors'].split(','))
#        super(MassUploadForm, self).save(*args, **kwargs)
#        