#from django.contrib.admin import autodiscover
from django import template

from ella.utils.installedapps import call_modules
from ella.newman.sites import site
from ella.newman.options import NewmanModelAdmin, NewmanInlineModelAdmin, NewmanStackedInline, NewmanTabularInline
from ella.newman.generic import BaseGenericInlineFormSet, GenericInlineModelAdmin, GenericStackedInline, GenericTabularInline

def autodiscover():
    call_modules(auto_discover=('newman_admin', 'admin',))

# add newman templatetags to builtin
template.add_to_builtins('ella.newman.templatetags.newman')

# newman url for object for other apps, FEs...
from ella.newman.utils import get_newman_url
