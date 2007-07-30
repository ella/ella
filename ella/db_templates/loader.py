from ella.db_templates import models
from django.template import TemplateDoesNotExist

def load_template_source(template_name, template_dirs=None):
    try:
        return (models.DbTemplate.objects.get(name=template_name).text, template_name)
    except models.DbTemplate.DoesNotExist:
        raise TemplateDoesNotExist, template_name

load_template_source.is_usable = models.DbTemplate._meta.installed

