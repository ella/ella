from ella.newman import site, GenericTabularInline
from ella.newman.licenses import LICENSED_MODELS
from ella.newman.licenses.models import License
from ella.newman.options import NewmanModelAdmin

class LicenseInlineAdmin(GenericTabularInline):
    model = License
    max_num = 1
    ct_field = 'ct'
    ct_fk_field = 'obj_id'

class LicenseAdmin(NewmanModelAdmin):
    pass

site.register(License, LicenseAdmin)
site.append_inline(LICENSED_MODELS, LicenseInlineAdmin)
