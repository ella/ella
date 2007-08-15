from os.path import dirname

from django.conf.urls.defaults import *
from django.contrib import admin

urlpatterns = patterns('',
    # Uncomment this for admin:
    (r'^admin/(.*)', admin.site.root),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': dirname(__file__) + '/media'}),
)
