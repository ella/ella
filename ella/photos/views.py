from django.utils import simplejson
from ella.photos import models
from django.conf import settings
from django.http import HttpResponse

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
    return HttpResponse(simplejson.dumps(content))
