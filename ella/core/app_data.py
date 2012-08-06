from django.utils import simplejson as json

from jsonfield.fields import JSONField

class AppDataField(JSONField):
    def __init__(self, *args, **kwargs):
        self.app_registry = kwargs.pop('app_registry', app_registry)
        kwargs.setdefault('default', '{}')
        kwargs.setdefault('editable', False)
        super(AppDataField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        """Convert string value to JSON and wrap it in AppDataContainerFactory"""
        if isinstance(value, basestring):
            try:
                val = json.loads(value, **self.load_kwargs)
                return AppDataContainerFactory(self.model, val, app_registry=self.app_registry)
            except ValueError:
                pass

        # app_data = {} should use AppDataContainerFactory
        if isinstance(value, dict) and not isinstance(value, AppDataContainerFactory):
            value = AppDataContainerFactory(self.model, value, app_registry=self.app_registry)

        return value

    def validate(self, value, model_instance):
        super(AppDataField, self).validate(value, model_instance)
        for k in value:
            data = value[k]
            if hasattr(data, 'validate'):
                data.validate(value, model_instance)


class AppDataContainerFactory(dict):
    def __init__(self, model,  *args, **kwargs):
        self.model = model
        self.app_registry = kwargs.pop('app_registry', app_registry)
        super(AppDataContainerFactory, self).__init__(*args, **kwargs)

    def __getitem__(self, name):
        # get the value, let the possible KeyError propagate
        val = super(AppDataContainerFactory, self).__getitem__(name)
        class_ = self.app_registry.get_class(name, self.model)
        if class_ is not None and not isinstance(val, class_):
            val = class_(val)
            self[name] = val

        return val

    def get(self, name, default=None):
        if name in self:
            return self[name]

        if default is None:
            return None

        class_ = self.app_registry.get_class(name, self.model)
        if class_ is not None:
            return class_(default)

        return default

class NamespaceConflict(Exception):
    pass

class NamespaceMissing(KeyError):
    pass

class NamespaceRegistry(object):
    """
    Global registry of app_specific storage classes in app_data field
    """
    def __init__(self, default_class=None):
        self.default_class = default_class
        self._reset()

    def _reset(self):
        # stuff registered by apps
        self._global_registry = {}
        self._model_registry = {}

        # TODO: overrides from settings
        self._global_overrides = {}
        self._model_overrides = {}

    def get_class(self, namespace, model):
        """
        Get class for namespace in given model, look into overrides first and
        then into registered classes.
        """
        for registry in (
            self._model_overrides.get(model, {}),
            self._global_overrides,
            self._model_registry.get(model, {}),
            self._global_registry
            ):
            if namespace in registry:
                return registry[namespace]
        return self.default_class

    def register(self, namespace, class_, model=None):
        registry = self._model_registry.setdefault(model, {}) if model is not None else self._global_registry
        if namespace in registry:
            raise NamespaceConflict(
                'Namespace %r already assigned to class %r%s.' % (
                    namespace,
                    registry[namespace],
                    '' if model is None else ' for model %s' % model._meta
                )
            )
        registry[namespace] = class_

    def unregister(self, namespace, model=None):
        registry = self._model_registry.setdefault(model, {}) if model is not None else self._global_registry
        if namespace not in registry:
            raise NamespaceMissing(
                'Namespace %r is not registered yet.' % namespace)

        del registry[namespace]

app_registry = NamespaceRegistry()
