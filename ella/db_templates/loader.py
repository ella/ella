from django.template import TemplateDoesNotExist
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.template.loader import BaseLoader

from ella.db_templates.models import DbTemplate
from ella.core.cache import get_cached_object


CT_DBTEMPLATE = ContentType.objects.get_for_model(DbTemplate)

class EllaDBTemplateLoader(BaseLoader):
    is_usable = DbTemplate._meta.installed
    
    def load_template_source(self, template_name, template_dirs=None):
        " template loader conforming to django's API "
        try:
            t = get_cached_object(CT_DBTEMPLATE, name=template_name, site__id=settings.SITE_ID)
            return (t.get_text(), template_name)
        except DbTemplate.DoesNotExist:
            raise TemplateDoesNotExist, template_name
    load_template_source.is_usable = DbTemplate._meta.installed

