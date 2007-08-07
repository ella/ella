# Create your views here.
from django.shortcuts import render_to_response
from django.utils import simplejson
from ella.photos import models
from django import template
from django.conf import settings

def format_photo_json(request, format, photo):
    try:
        photo = models.Photo.objects.get(pk=photo)
        format = models.Format.objects.get(pk=format)
        content = {
            'error': False,
            'image':settings.MEDIA_URL + photo.image,
            'width':photo.width,
            'height': photo.height,
            'format_width':format.max_width,
            'format_height':format.max_height
}
    except (models.Photo.DoesNotExist, models.Format.DoesNotExist):
        content = {'error':True}
    return render_to_response('json.html', {'content':simplejson.dumps(content)})
