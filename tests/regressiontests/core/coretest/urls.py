from django.conf.urls.defaults import *

# Uncomment this for admin:
from django.contrib import admin

urlpatterns = patterns('',
    (r'^admin/(.*)', admin.site.root),
    ('^', include('ella.core.urls')),
)
