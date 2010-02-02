from django.conf.urls.defaults import patterns, url

from ella.core.custom_urls import resolver
from ella.media.views import player_playlist_for_id, player_playlist

urlpatterns = patterns('',
    url(r'^$', player_playlist, name='ella-media-playlist'),
    url(r'^(?P<embed>embed)/$', player_playlist, name='ella-media-playlist'),
    url(r'^playlist/(\d+)/$', player_playlist_for_id, name='ella-media-playlist-for-id'),
)

resolver.register(urlpatterns, prefix='playlist')
