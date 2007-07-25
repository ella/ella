from django.conf.urls.defaults import *

# Uncomment this for admin:
#from django.contrib import admin

urlpatterns = patterns('',
    ('^', include('ella.core.urls')),
)
