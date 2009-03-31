from django.conf.urls.defaults import *

from djangobaselibrary.sample import views

urlpatterns = patterns('',
    url(r'^$', views.homepage, name='djangobaselibrary-homepage'),
)

