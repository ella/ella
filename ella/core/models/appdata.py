'''
Created on 3.8.2012

@author: xaralis
'''


class AppDataContainer(dict):
    def __init__(self, obj, app_label, *args, **kwargs):
        self.obj = obj
        self.app_label = app_label
        super(*args, **kwargs)


class NamespaceRegistry(dict):
    class NamespaceConflict(Exception):
        pass

    class NamespaceMissing(KeyError):
        pass

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


class AppDataMixin(object):
    app_data_registry = NamespaceRegistry()

    def get_app_data(self, namespace):
        class_ = self.app_data_registry.get(namespace, AppDataContainer)
        return class_(self, self._meta.app_label, self.app_data)

    def set_app_data(self, namespace, data):
        self.app_data[namespace] = data
