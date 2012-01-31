from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^tags/', include('ella.ellatagging.urls')),
    (r'^', include('ella.core.urls')),
)
