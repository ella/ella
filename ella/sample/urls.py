from django.conf.urls.defaults import *

from ella.sample import views

urlpatterns = patterns('',
    url(r'^$', views.homepage, name='ella-homepage'),
)

