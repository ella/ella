from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module

def import_module_member(modstr, noun=''):
    module, attr = modstr.rsplit('.', 1)
    try:
        mod = import_module(module)
    except ImportError, e:
        raise ImproperlyConfigured('Error importing %s %s: "%s"' % (noun, modstr, e))
    try:
        member = getattr(mod, attr)
    except AttributeError, e:
        raise ImproperlyConfigured('Error importing %s %s: "%s"' % (noun, modstr, e))
    return member


