from django.conf.urls.defaults import *
from django.contrib import admin

urlpatterns = patterns('',
    # Example:
    # (r'^gallerytest/', include('gallerytest.foo.urls')),

    # Uncomment this for admin:
#     (r'^admin/', include('django.contrib.admin.urls')),
    (r'^admin/(.*)', admin.site.root),
)
