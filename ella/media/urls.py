from django.conf.urls.defaults import patterns, url

from ella.core.custom_urls import resolver
from ella.media.views import player_playlist_for_id

urlpatterns = patterns('',
    url(r'^playlist/(\d+)/$', player_playlist_for_id, name='ella-media-playlist'),
)

resolver.register(urlpatterns, prefix='playlist')

