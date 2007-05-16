from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^~', include('nc.auth.urls')),
    (r'^', include('djangoutils.auth_sample.urls')),
)
