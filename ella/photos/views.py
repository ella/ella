from django.utils import simplejson
from django.conf import settings
from django.http import HttpResponse

from ella.photos import models
from ella.core.cache.utils import get_cached_object
def format_photo_json(request, format, photo):
    try:
        photo = get_cached_object(models.Photo, pk=photo)
        format = get_cached_object(models.Format, pk=format)
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
