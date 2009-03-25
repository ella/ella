from django.contrib.admin import autodiscover

from ella.newman.sites import site
from ella.newman.options import NewmanModelAdmin, NewmanInlineModelAdmin, NewmanStackedInline, NewmanTabularInline
from ella.newman.generic import BaseGenericInlineFormSet, GenericInlineModelAdmin, GenericStackedInline, GenericTabularInline

# need to import filterspecs in __init__. filterspecs module shoud clean filters before they're assigned to ModelAdmins
#import ella.newman.filterspecs
