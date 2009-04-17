from django.conf.urls.defaults import *

from ella.core.custom_urls import dispatcher
from ella.media import views

urlpatterns = patterns('',
    url(r'^playlist/(\d+)/$', views.player_playlist_for_id, name='ella_media_playlist'),
)

dispatcher.register('playlist', views.player_playlist)

