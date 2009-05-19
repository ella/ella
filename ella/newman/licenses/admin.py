from django.contrib import admin
from ella.newman.licenses.models import License

class LicenseInlineAdmin(admin.TabularInline):
    model = License
    max_num = 1
    ct_field = 'ct'
    ct_fk_field = 'obj_id'

class LicenseAdmin(admin.ModelAdmin):
    pass

admin.site.register(License, LicenseAdmin)
