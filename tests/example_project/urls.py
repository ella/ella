from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # serve static files
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT, 'show_indexes': True }),

    # reverse url lookups
#    (r'^', include('djangobaselibrary.sample.urls')),

)

