from ella import newman

from ella.catlocks.models import CategoryLock

class CategoryLockAdmin(newman.NewmanModelAdmin):
    raw_id_fields = ('category',)

newman.site.register(CategoryLock, CategoryLockAdmin)


