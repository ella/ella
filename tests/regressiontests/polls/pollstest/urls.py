from django.conf.urls.defaults import *
from django.contrib import admin

urlpatterns = patterns('',
    (r'^admin/(.*)', admin.site.root),
    (r'^polls/', include('ella.polls.urls')),
    (r'^', include('ella.core.urls')),
)
