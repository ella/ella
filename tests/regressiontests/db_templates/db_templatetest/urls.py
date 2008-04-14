from django.conf.urls.defaults import *

# Uncomment this for admin:
from django.contrib import admin

urlpatterns = patterns('',
    # Example:
    # (r'^db_templates/', include('db_templates.foo.urls')),

    # Uncomment this for admin docs:
    #(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment this for admin:
    ('^admin/(.*)', admin.site.root),
)
