from django.conf.urls.defaults import *

# Uncomment this for admin:
#from django.contrib import admin

urlpatterns = patterns('',
    # Special template for PhotoFormat cropper AJAX information JSON:
    (r'^admin/photos/json/([0-9]+)/([0-9]+)/$', 'ella.photos.views.format_photo_json'),

)
