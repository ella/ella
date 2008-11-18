from ella.core.custom_urls import dispatcher
from ella.media.views import player_playlist

dispatcher.register('playlist', player_playlist)
