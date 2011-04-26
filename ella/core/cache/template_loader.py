import warnings

from django.core.exceptions import ImproperlyConfigured
from django.template import TemplateDoesNotExist, loader, Context
from django.conf import settings
from django.http import HttpResponse

from ella.core.cache.utils import cache_this
from ella.core.cache.invalidate import CACHE_DELETER


CACHE_TIMEOUT = getattr(settings, 'CACHE_TIMEOUT', 10*60)
template_source_loaders = None


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
                warnings.warn((
                    "Your TEMPLATE_LOADERS setting includes %r, but your Python installation "
                    "doesn't support that type of template loading. Consider removing that line from TEMPLATE_LOADERS.") % path)
            else:
                template_source_loaders.append(func)

    return get_cache_template(template_name, template_dirs)
load_template_source.is_usable = True

def get_key(func, template_name, template_dirs=None):
    return 'ella.core.cache.template_loader:%d:%s' % (settings.SITE_ID, template_name,)

def invalidate_cache(key, template_name, template_dirs=None):
    from ella.db_templates.models import DbTemplate
    if DbTemplate._meta.installed:
        CACHE_DELETER.register_test(DbTemplate, "name:%s" % template_name, key)

@cache_this(get_key, invalidate_cache)
def get_cache_template(template_name, template_dirs):
    for l in template_source_loaders:
        try:
            source, display_name = l(template_name, template_dirs)
            return (source, display_name)
        except TemplateDoesNotExist:
            pass
    raise TemplateDoesNotExist, template_name

def get_sel_template_key(func, template_list):
    return 'ella.core.cache.template_loader.select_template:%d:%s' % (settings.SITE_ID, ','.join(template_list))

@cache_this(get_sel_template_key)
def find_template(template_list):
    for template in template_list:
        try:
            #source, origin = loader.find_template_source(template)
            source, origin = loader.find_template(template) # Django 1.3
            return (source, origin, template)
        except loader.TemplateDoesNotExist:
            pass
    raise loader.TemplateDoesNotExist, ', '.join(template_list)

def select_template(template_list):
    source, origin, template_name = find_template(template_list)
    return source
    #return loader.get_template_from_string(source, origin, template_name)

def render_to_response(template_name, dictionary=None, context_instance=None, content_type=None):
    if isinstance(template_name, (list, tuple)):
        t = select_template(template_name)
    else:
        t = loader.get_template(template_name)
    dictionary = dictionary or {}

    if context_instance:
        context_instance.update(dictionary)
    else:
        context_instance = Context(dictionary)

    return HttpResponse(t.render(context_instance), content_type=content_type)

