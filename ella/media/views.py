from django.http import Http404
from django.shortcuts import render_to_response
from django.template.context import RequestContext

class PlayerPlaylist(object):
    """
    Renders xml playlist for object with media
    """
    def __init__(self):
        self.listeners = []

    def register(self, callback):
        """
        Regiter listener if your app needs
        change context or use custom template

        new_tempalate = listener(request, bits, context, template)
        """
        self.listeners.append(callback)

    def __call__(self, request, context, **kwargs):
        """
        This function is called by ella custom urls
        """
        object = context['object']
        try:
            media = object.media
        except AttributeError:
            # This content type has no media
            raise Http404

        template = 'page/media/playlist.xml'
        context['media'] = media

        for listener in self.listeners:
            new_template = listener(request, context, template, **kwargs)
            if new_template:
                template = new_template
        response = render_to_response(template, RequestContext(request, context))
        response['content-type'] = 'text/xml; charset=utf-8';
        return response

# this instance is registred in ella custom urls
player_playlist = PlayerPlaylist()

def player_playlist_for_id(request, id):
    try:
        media = Media.objects.get(pk=id)
    except Media.DoesNotExist:
        raise Http404

    # TODO: remove this hack for PlayerPlaylist
    media.media = media

    context = {'object': media,}
    player_playlist = PlayerPlaylist()

    return player_playlist(request, [], context)

