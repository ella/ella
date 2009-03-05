from ella.newman import site
from ella.newman.generic import GenericTabularInline
from ella.newman.licenses.models import License

LICENSED_MODELS = (
    'photos.photo',
)

class LicenseInlineAdmin(GenericTabularInline):
    model = License
    extra = 1
    max_num = 1
    ct_field = 'ct'
    ct_fk_field = 'obj_id'

site.register(License)
site.append_inline(LICENSED_MODELS, LicenseInlineAdmin)
