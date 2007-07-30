from django.contrib.contenttypes.models import ContentType
from django.http import Http404

from ella.core.custom_urls import dispatcher

UPDOWN = {'up' : 1, 'down' : -1}

def rate(request, bits, context):
    from ella.ratings.views import do_rate

    if len(bits) != 1 or bits[0] not in UPDOWN:
        raise Http404

    return do_rate(request, ContentType.objects.get_for_model(context['object']), context['object'], UPDOWN[bits[0]])

dispatcher.register('rate',  rate)
