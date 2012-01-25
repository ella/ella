from django.conf.urls.defaults import *

from django.contrib import admin

from test_ella.urls import urlpatterns

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
) + urlpatterns
