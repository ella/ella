__doc__ = """ella.newman is next (3rd ?) generation of admin for Ella"""
from ella.newman.sites import NewmanSite, site

# need to import filterspecs in __init__. filterspecs module shoud clean filters before they're assigned to ModelAdmins
import ella.newman.filterspecs
import ella.newman.views
