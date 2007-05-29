from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^ratings/', include('nc.ratings.urls')),
)
