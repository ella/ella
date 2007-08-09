from django.conf.urls.defaults import *
from komments.sample.views import *


urlpatterns = patterns('',
        url(r'^list/apples/$', list_apples),
        url(r'^list/apples/(?P<id>[^/]+)/$', list_apple),
)

