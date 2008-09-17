from django.contrib import admin

from ella.catlocks.models import CategoryLock

class CategoryLockAdmin(admin.ModelAdmin):
    raw_id_fields = ('category',)

admin.site.register(CategoryLock, CategoryLockAdmin)