from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings


urlpatterns = patterns('',
    (r'^upload/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.UPLOAD_ROOT, 'show_indexes': True}),
    (r'^admin/(.*)', admin.site.root),
    (r'^', include('ella.core.urls')),
)

