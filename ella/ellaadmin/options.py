from django.contrib import admin

from ella.ellaadmin import widgets


def mixin_ella_admin(admin_class):
    bases = list(admin_class.__bases__)
    admin_class.__bases__ = tuple(bases + [EllaAdminOptionsMixin])

def register_ella_admin(func):
    def _register(self, model_or_iterable, admin_class=None, **options):
        admin_class = admin_class or admin.ModelAdmin
        mixin_ella_admin(admin_class)
        return func(self, model_or_iterable, admin_class, **options)
    return _register

class EllaAdminSite(admin.AdminSite):
    def __init__(self):
        self._registry = admin.site._registry
        for options in self._registry.values():
            mixin_ella_admin(options.__class__)
        site.register = register_ella_admin(site.register)

class EllaAdminOptionsMixin(admin.ModelAdmin):
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'target_ct':
            kwargs['widget'] = widgets.ContentTypeWidget
        if db_field.name == 'target_id':
            kwargs['widget'] = widgets.ForeignKeyRawIdWidget
        if db_field.name == 'source_ct':
            kwargs['widget'] = widgets.ContentTypeWidget
        if db_field.name == 'source_id':
            kwargs['widget'] = widgets.ForeignKeyRawIdWidget
        return super(EllaAdminOptionsMixin, self).formfield_for_dbfield(db_field, **kwargs)

site = EllaAdminSite()


