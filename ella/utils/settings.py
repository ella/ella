from django.utils.importlib import import_module
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class Settings(object):
    """
    Simple wrapper around config. Read setting value from the projects'
    setting.py or from the given module. If you specify prefix, put
    setting in your projects' setting.py with prefix: PREFIX_<CONF_OPTION>.
    """

    def __init__(self, module_name, prefix=''):
        self.module = import_module(module_name)
        self.prefix = prefix

    def __getattr__(self, name):
        if self.prefix:
            p_name = '_'.join((self.prefix, name))
        else:
            p_name = name

        if hasattr(settings, p_name):
            return getattr(settings, p_name)

        try:
            return getattr(self.module, name)
        except AttributeError:
            raise ImproperlyConfigured("'%s' setting doesn't exist in your settings module '%s'." % (p_name, self.module.__name__))

    def __dir__(self):
        return dir(self.module) + dir(settings)
