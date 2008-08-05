
from django.shortcuts import render_to_response, get_object_or_404

from ella.media.models import Media

def player_playlist(request, slug):
    object = get_object_or_404(Media, slug=slug)
    response = render_to_response('playlist.xml', {'object':object})
    response['content-type'] = 'text/xml; charset=utf-8';
    return response