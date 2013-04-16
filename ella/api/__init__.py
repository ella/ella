from serialization import object_serializer, response_serializer, PARTIAL, FULL
from .conf import api_settings

def render_as_api(request, obj):
    if api_settings.ENABLED:
        for mimetype in (a.split(';')[0] for a in request.META.get('HTTP_ACCEPT', '').split(',')):
            if response_serializer.serializable(mimetype):
                return response_serializer.serialize(object_serializer.serialize(request, obj, FULL), mimetype)
