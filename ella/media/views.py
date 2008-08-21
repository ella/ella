
from django.shortcuts import render_to_response, get_object_or_404
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _

from ella.media.models import Media

def player_playlist(request, slug):
    media = get_object_or_404(Media, slug=slug)
    cx = {
        'media': media,
        'sendmail_url': '%s%s/%s/' % (media.get_absolute_url(), slugify(_('send mail')), slugify(_('xml')))
}
    response = render_to_response('playlist.xml', cx)
    response['content-type'] = 'text/xml; charset=utf-8';
    return response
