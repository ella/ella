from ella.newman import site
from ella.newman.options import GenericTabularInline
from ella.newman.licenses.models import License

class LicenseInlineAdmin(GenericTabularInline):
    model = License
    extra = 1
    max_num = 1 # TODO: we need only 1 licence per object
    ct_field = 'ct'
    ct_fk_field = 'obj_id'

site.register(License)
