from django.utils import simplejson as json

from jsonfield.fields import JSONField


class AppDataField(JSONField):
    """
    Creates `app_data_registry` on the class and also ensures that
    right `AppDataContainer` subclass is returned using
    `AppDataContainerFactory` object.
    """
    def contribute_to_class(self, cls, name):
        super(AppDataField, self).contribute_to_class(cls, name)
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
        self.model = model
        super(AppDataContainerFactory, self).__init__(*args, **kwargs)

    def __getitem__(self, name):
        class_ = self.model.app_data_registry.get(name, AppDataContainer)

        if name in self:
            val = super(AppDataContainerFactory, self).__getitem__(name)
        else:
            val = {}

        return class_(self.model, val)


class AppDataContainer(dict):
    """
    Base class for creating custom app data containers.
    """
    def __init__(self, model, *args, **kwargs):
        self.model = model
        super(AppDataContainer, self).__init__(*args, **kwargs)


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


