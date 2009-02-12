__doc__ = """ella.newman is next (3rd ?) generation of admin for Ella"""

# need to import filterspecs in __init__. filterspecs module shoud clean filters before they're assigned to ModelAdmins
import ella.newman.filterspecs

from ella.newman.sites import NewmanSite, site
from ella.newman.options import NewmanModelAdmin
