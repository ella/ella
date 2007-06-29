from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^ratings/', include('ella.ratings.urls')),
)
