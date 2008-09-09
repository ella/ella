
from django.http import Http404

from django.shortcuts import render_to_response, get_object_or_404
from django.template.defaultfilters import slugify
from django.template.context import RequestContext
from django.utils.translation import ugettext as _

from ella.media.models import Media

def player_playlist(request, bits, context):
    object = context['object']
    try:
        media = object.media
    except AttributeError:
        # This content type has no media
        raise Http404

    cx = {
        'media': media,
        'object' : object,
        'sendmail_url': '%s%s/%s/' % (media.get_absolute_url(), slugify(_('send mail')), slugify(_('xml')))
}
    response = render_to_response('playlist.xml', RequestContext(request, cx))
    response['content-type'] = 'text/xml; charset=utf-8';
    return response


