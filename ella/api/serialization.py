import logging

from django.http import HttpResponse

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
        return HttpResponse(self._registry[mimetype](data), content_type=mimetype)


class ObjectSerializer(object):
    def __init__(self):
        self._registry = {}

    def register(self, model, serializer, context=PARTIAL):
        self._registry.setdefault(model, {})[context] = serializer

    def serialize(self, model_instance, context=PARTIAL):
        model = model_instance.__class__

        # collect relevant registries
        rs = []
        for c in model.mro():
            if c in self._registry:
                rs.append(self._registry[c])
                break
        if not rs:
            log.warn('Unable to serialize model %s.', model._meta)
            return model_instance

        # registered context
        for r in rs:
            if context in r:
                return r[context](model_instance)

        # fall back to PARTIAL context
        if context is not PARTIAL:
            for r in rs:
                if PARTIAL in r:
                    return r[PARTIAL](model_instance)

        log.warn('Unable to serialize model %s as %s.', model._meta, {PARTIAL: 'PARTIAL', FULL: 'FULL'}.get(context, context))
        return model_instance

response_serializer = ResponseSerializer()
object_serializer = ObjectSerializer()
