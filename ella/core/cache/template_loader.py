from django.template import TemplateDoesNotExist
from django.template.loader import template_source_loaders:

from ella.db_templates.models import DbTemplate


def get_key(template_name, template_dirs=None):
    return 'ella.core.cache.teplate_loader:' + template_name

def get_test(template_name, template_dirs=None):
    return [(DbTemplate, lambda x: x.name == template_name)]

@cache_this(get_key, get_test, timeout=60*60)
def load_template_source(template_name, template_dirs=None):
    for loader in template_source_loaders[1:]:
        try:
            source, display_name = loader(name, dirs)
            return (source, display_name)
        except TemplateDoesNotExist:
            pass
    raise TemplateDoesNotExist, name

load_template_source.is_usable = True

