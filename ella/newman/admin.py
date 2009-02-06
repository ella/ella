#from django.contrib import admin

from ella.newman.sites import site
from ella.newman import models as m
from ella.ellaadmin.options import EllaModelAdmin

class DevMessageAdmin(EllaModelAdmin):
    list_display = ('title', 'author', 'version', 'ts',)
    prepopulated_fields = {'slug': ('title',)}

    def save_model(self, request, obj, form, change):
        if not obj.id:
            obj.author = request.user
        obj.save()


class HelpItemAdmin(EllaModelAdmin):
    list_display = ('__unicode__',)
    list_filter = ('ct', 'lang',)
    list_select_related = False


class GroupFavAdmin(EllaModelAdmin):
    list_display = ('__unicode__',)
    list_filter = ('ct', 'group',)


site.register(m.DevMessage, DevMessageAdmin)
site.register(m.AdminHelpItem, HelpItemAdmin)
site.register(m.AdminGroupFav, GroupFavAdmin)
