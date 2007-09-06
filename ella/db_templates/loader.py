from django.template import TemplateDoesNotExist
from django.contrib.contenttypes.models import ContentType

from ella.db_templates.models import DbTemplate
from ella.core.cache import get_cached_object

CT_DBTEMPLATE = ContentType.objects.get_for_model(DbTemplate)

def load_template_source(template_name, template_dirs=None):
    try:
        return (get_cached_object(CT_DBTEMPLATE, name=template_name).text, template_name)
    except DbTemplate.DoesNotExist:
        raise TemplateDoesNotExist, template_name

load_template_source.is_usable = DbTemplate._meta.installed

