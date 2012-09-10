from django.dispatch import Signal
from django.utils.itercompat import is_iterable
from django.conf import settings
from django.utils.importlib import import_module
from django.utils.module_loading import module_has_submodule

app_modules_loaded = Signal()

INSTALLED_APPS_REGISTER = {}

def register(app_name, modules):
    """
    simple module registering for later usage
    we don't want to import admin.py in models.py
    """
    global INSTALLED_APPS_REGISTER
    mod_list = INSTALLED_APPS_REGISTER.get(app_name, [])

    if isinstance(modules, basestring):
        mod_list.append(modules)
    elif is_iterable(modules):
        mod_list.extend(modules)

    INSTALLED_APPS_REGISTER[app_name] = mod_list


def call_modules(auto_discover=()):
    """
    this is called in project urls.py
    for registering desired modules (eg.: admin.py)
    """
    for app in settings.INSTALLED_APPS:
        modules = set(auto_discover)
        if app in INSTALLED_APPS_REGISTER:
            modules.update(INSTALLED_APPS_REGISTER[app])
        for module in modules:
            mod = import_module(app)
            try:
                import_module('%s.%s' % (app, module))
                inst = getattr(mod, '__install__', lambda: None)
                inst()
            except:
                if module_has_submodule(mod, module):
                    raise
    app_modules_loaded.send(sender=None)

