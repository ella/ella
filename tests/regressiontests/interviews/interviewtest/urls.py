from django.conf.urls.defaults import *
from django.contrib import admin

urlpatterns = patterns('',
    (r'^admin/(.*)', admin.site.root),
    (r'^interviews/', include('ella.interviews.urls')),
    (r'^', include('ella.core.urls')),
)
