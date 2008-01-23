from django.conf.urls.defaults import *
from django.contrib import admin
from django import VERSION


urlpatterns = patterns('',
    ('^admin/(.*)', admin.site.root),
    ('^', include('ella.core.urls')),
)

