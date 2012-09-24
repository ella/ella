import logging

__all__ = ['response_serializer', 'object_serializer', 'TOP_LEVEL', 'RELATED']

log = logging.getLogger('ella.api.serialization')


TOP_LEVEL = object()
RELATED = object()

class ResponseSerializer(object):
    def __init__(self):
        self._registry = {}

    def register(self, mimetype, serializer):
        self._registry[mimetype] = serializer

    def serializable(self, mimetype):
        return mimetype in self._registry

    def serialize(self, data, mimetype):
        return self._registry[mimetype](data)


class ObjectSerializer(object):
    def __init__(self):
        self._registry = {}

    def register(self, model, serializer, context=RELATED):
        self._registry.setdefault(model, {})[context] = serializer

    def serialize(self, model_instance, context=RELATED):
        model = model_instance.__class__

        # collect relevant registries
        rs = []
        for c in model.mro():
            if c in self._registry:
                rs.append(self._registry[c])
                break
        if not rs:
            log.warn('Unable to serialize model %s.', model._meta)
            return None

        # registered context
        for r in rs:
            if context in r:
                return r[context](model_instance)

        # fall back to RELATED context
        if context is not RELATED:
            for r in rs:
                if RELATED in r:
                    return r[RELATED](model_instance)

        log.warn('Unable to serialize model %s as %s.', model._meta, {RELATED: 'RELATED', TOP_LEVEL: 'TOP_LEVEL'}.get(context, context))
        return None

response_serializer = ResponseSerializer()
object_serializer = ObjectSerializer()
