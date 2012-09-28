import logging

from django.http import HttpResponse
from django.utils.cache import patch_vary_headers

__all__ = ['response_serializer', 'object_serializer', 'FULL', 'PARTIAL']

log = logging.getLogger('ella.api.serialization')


FULL = object()
PARTIAL = object()

class ResponseSerializer(object):
    def __init__(self):
        self._registry = {}

    def register(self, mimetype, serializer):
        self._registry[mimetype] = serializer

    def serializable(self, mimetype):
        return mimetype in self._registry

    def serialize(self, data, mimetype):
        response = HttpResponse(self._registry[mimetype](data), content_type=mimetype)
        # signalize to the cache middleware that this responds depends on the Accept http header
        patch_vary_headers(response, ('Accept', ))
        return response

class ObjectSerializer(object):
    def __init__(self):
        self._registry = {}

    def register(self, cls, serializer, context=PARTIAL):
        self._registry.setdefault(cls, {})[context] = serializer

    def serialize(self, data, context=PARTIAL):
        # collect relevant registries
        rs = []
        for c in data.__class__.mro():
            if c in self._registry:
                rs.append(self._registry[c])
                break
        if not rs:
            return data

        # registered context
        for r in rs:
            if context in r:
                return r[context](data)

        # fall back to PARTIAL context
        if context is not PARTIAL:
            for r in rs:
                if PARTIAL in r:
                    return r[PARTIAL](data)

        return data

response_serializer = ResponseSerializer()
object_serializer = ObjectSerializer()
