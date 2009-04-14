from ella.newman import site, GenericTabularInline
from ella.newman.licenses.models import License
from ella.newman.options import NewmanModelAdmin

LICENSED_MODELS = (
    'photos.photo',
)

class LicenseInlineAdmin(GenericTabularInline):
    model = License
    max_num = 1
    ct_field = 'ct'
    ct_fk_field = 'obj_id'

class LicenseAdmin(NewmanModelAdmin):
    pass

site.register(License, LicenseAdmin)
site.append_inline(LICENSED_MODELS, LicenseInlineAdmin)
