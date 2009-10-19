from django.contrib import admin

from ella.newman import models as m

class DevMessageAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'version', 'ts',)
    prepopulated_fields = {'slug': ('title',)}

    def save_model(self, request, obj, form, change):
        if not obj.id:
            obj.author = request.user
        obj.save()


class HelpItemAdmin(admin.ModelAdmin):
    list_display = ('__unicode__',)
    list_filter = ('ct', 'lang',)
    list_select_related = False
    rich_text_fields = {'': ('long',)}


class CategoryUserRoleAdmin(admin.ModelAdmin):
    list_filter = ('user', 'group',)
    list_display = ('user', 'group',)


admin.site.register(m.DevMessage, DevMessageAdmin)
admin.site.register(m.AdminHelpItem, HelpItemAdmin)
admin.site.register(m.CategoryUserRole, CategoryUserRoleAdmin)
