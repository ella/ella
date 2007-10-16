from django.template import TemplateDoesNotExist
from django.conf import settings

from ella.core.cache.utils import cache_this

template_source_loaders = None

def get_key(func, template_name, template_dirs=None):
    return 'ella.core.cache.teplate_loader:%d:%s' % (settings.SITE_ID, template_name,)

def get_test(template_name, template_dirs=None):
    from ella.db_templates.models import DbTemplate
    if DbTemplate._meta.installed:
        return [(DbTemplate, lambda x: x.name == template_name)]
    return []

def load_template_source(template_name, template_dirs=None):
    global template_source_loaders
    if template_source_loaders is None:
        template_source_loaders = []
        for path in settings.CACHE_TEMPLATE_LOADERS:
            i = path.rfind('.')
            module, attr = path[:i], path[i+1:]
            try:
                mod = __import__(module, globals(), locals(), [attr])
            except ImportError, e:
                raise ImproperlyConfigured, 'Error importing template source loader %s: "%s"' % (module, e)
            try:
                func = getattr(mod, attr)
            except AttributeError:
                raise ImproperlyConfigured, 'Module "%s" does not define a "%s" callable template source loader' % (module, attr)
            if not func.is_usable:
                import warnings
                warnings.warn("Your TEMPLATE_LOADERS setting includes %r, but your Python installation doesn't support that type of template loading. Consider removing   +that line from TEMPLATE_LOADERS." % path)
            else:
                template_source_loaders.append(func)

    return get_cache_teplate(template_name, template_dirs)
load_template_source.is_usable = True

@cache_this(get_key, get_test, timeout=10*60)
def get_cache_teplate(template_name, template_dirs):
    for loader in template_source_loaders:
        try:
            source, display_name = loader(template_name, template_dirs)
            return (source, display_name)
        except TemplateDoesNotExist:
            pass
    raise TemplateDoesNotExist, template_name


