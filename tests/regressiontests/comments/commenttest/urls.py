from django.conf.urls.defaults import *
from django.contrib import admin
from django import VERSION


urlpatterns = patterns('',
    ('^admin/(.*)', admin.site.root),
    (r'^comments/', include('ella.comments.urls')),
    (r'^sample/', include('commenttest.sample.urls')),
    ('^', include('ella.core.urls')),
)

