#from django.contrib.admin import autodiscover

from ella.utils.installedapps import call_modules
from ella.newman.sites import site
from ella.newman.options import NewmanModelAdmin, NewmanInlineModelAdmin, NewmanStackedInline, NewmanTabularInline
from ella.newman.generic import BaseGenericInlineFormSet, GenericInlineModelAdmin, GenericStackedInline, GenericTabularInline

def autodiscover():
    call_modules(auto_discover=('newman_admin',))
