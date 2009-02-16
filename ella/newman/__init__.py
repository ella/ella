from django.contrib.admin import autodiscover
from ella.newman.sites import site
from ella.newman.options import NewmanModelAdmin

# need to import filterspecs in __init__. filterspecs module shoud clean filters before they're assigned to ModelAdmins
#import ella.newman.filterspecs
