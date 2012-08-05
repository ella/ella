from django.utils import simplejson as json

from jsonfield.fields import JSONField


class AppDataField(JSONField):
    """
    Creates `app_data_registry` on the class and also ensures that
    right `AppDataContainer` subclass is returned using
    `AppDataContainerFactory` object.
    """
    # FIXME: add validation hooks
    def contribute_to_class(self, cls, name):
        super(AppDataField, self).contribute_to_class(cls, name)
        # FIXME: this blows up if you have more than one app_data field, also possible name conflict
        cls.app_data_registry = NamespaceRegistry()

    def to_python(self, value):
        """Convert string value to JSON"""
        if isinstance(value, basestring):
            try:
                val = json.loads(value, **self.load_kwargs)
                return AppDataContainerFactory(self.model, val)
            except ValueError:
                pass
        return value


class AppDataContainerFactory(dict):
    def __init__(self, model, *args, **kwargs):
        # FIXME: you really want to be passing model instance if possible, not class
        self.model = model
        super(AppDataContainerFactory, self).__init__(*args, **kwargs)

    def __getitem__(self, name):
        # FIXME: what if I want to store list, string or a number? don't default to something controlled, just raise KeyError
        # FIXME: don't modify __getitem__, instead only wrap things in appropriate class in __getitem__ and use .get_or_create() for this logic.
        class_ = self.model.app_data_registry.get(name, AppDataContainer)

        if name in self:
            val = super(AppDataContainerFactory, self).__getitem__(name)
        else:
            # FIXME: if not in self, add it there!
            val = {}

        return class_(self.model, val)


class AppDataContainer(dict):
    """
    Base class for creating custom app data containers.
    """
    def __init__(self, model, *args, **kwargs):
        self.model = model
        super(AppDataContainer, self).__init__(*args, **kwargs)


# FIXME: don't extend dict, use dict internally to store the registry
class NamespaceRegistry(dict):
    """
    Registry which is bound to each `AppDataMixin` class that holds registered
    namespaces and their respective `AppDataContainer` subclasses.
    """
    class NamespaceConflict(Exception):
        pass

    class NamespaceMissing(KeyError):
        pass

    def is_registered(self, namespace):
        return namespace in self

    def register(self, namespace, class_):
        # FIXME: add a global registry somewhere that also supports per-project overriding via settings
        # FIXME: have the global registry allow apps to specify/override continers per model class or globally
        if namespace in self:
            raise self.NamespaceConflict(
                'Namespace %r already assigned to class %r' % (
                    namespace, self.__getitem__(namespace)))

        self.__setitem__(namespace, class_)
        return class_

    def unregister(self, namespace):
        if namespace not in self:
            raise self.NamespaceMissing(
                'Namespace %r is not registered yet.' % namespace)

        self.__delitem__(namespace)


