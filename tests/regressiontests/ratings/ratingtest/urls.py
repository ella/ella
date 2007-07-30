from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^ratings/', include('ella.ratings.urls')),
    (r'^', include('ella.core.urls')),
)
