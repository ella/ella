import datetime

from django.db import models
from django.utils.translation import ugettext as _
from django.contrib import admin

from ella.newman.sites import site
from ella.newman import models as m
from ella.ellaadmin.options import EllaModelAdmin
from ella.newman.filterspecs import filter_spec

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


class CategoryUserRoleOptions(admin.ModelAdmin):
    list_filter = ('user', 'group', 'category',)
    list_display = ('user', 'group', 'category',)


site.register(m.DevMessage, DevMessageAdmin)
site.register(m.AdminHelpItem, HelpItemAdmin)
site.register(m.AdminGroupFav, GroupFavAdmin)
site.register(m.CategoryUserRole, CategoryUserRoleOptions)


# Example of custom registered DateField filter. Filter is inserted to the beginning of filter chain.
@filter_spec(lambda f: isinstance(f, models.DateField))
def customized_date_field_filter(fspec):
    params = fspec.params; model = fspec.model; model_admin = fspec.model_admin; field_path = fspec.field_path
    fspec.field_generic = '%s__' % fspec.field_path
    fspec.date_params = dict([(k, v) for k, v in params.items() if k.startswith(fspec.field_generic)])
    today = datetime.date.today()
    one_week_ago = today - datetime.timedelta(days=7)
    today_str = isinstance(fspec.field, models.DateTimeField) and today.strftime('%Y-%m-%d 23:59:59') or today.strftime('%Y-%m-%d')

    fspec.links = (
        (_('Any date'), {}),
        (_('Today'), {'%s__year' % fspec.field_path: str(today.year),
                   '%s__month' % fspec.field_path: str(today.month),
                   '%s__day' % fspec.field_path: str(today.day)}),
        (_('Past 7 days'), {'%s__gte' % fspec.field_path: one_week_ago.strftime('%Y-%m-%d'),
                         '%s__lte' % fspec.field_path: today_str}),
        (_('This month'), {'%s__year' % fspec.field_path: str(today.year),
                         '%s__month' % fspec.field_path: str(today.month)}),
        (_('This year'), {'%s__year' % fspec.field_path: str(today.year)})
)
    return True
