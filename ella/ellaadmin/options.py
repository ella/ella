from django.contrib import admin
from django import newforms as forms

from ella.ellaadmin import widgets


def mixin_ella_admin(admin_class):
    if admin_class == admin.ModelAdmin:
        return ExtendedModelAdmin

    if EllaAdminOptionsMixin in admin_class.__bases__:
        # TODO: recursive traversal to parents...
        return admin_class

    bases = list(admin_class.__bases__)
    admin_class.__bases__ = tuple([EllaAdminOptionsMixin] + bases)
    return admin_class

def register_ella_admin(func):
    def _register(self, model_or_iterable, admin_class=None, **options):
        admin_class = admin_class or admin.ModelAdmin
        admin_class = mixin_ella_admin(admin_class)
        for inline in admin_class.inlines:
            inline = mixin_ella_admin(inline)
        return func(self, model_or_iterable, admin_class, **options)
    return _register


class EllaAdminSite(admin.AdminSite):
    def __init__(self):
        self._registry = admin.site._registry
        for options in self._registry.values():
            options.__class__ = mixin_ella_admin(options.__class__)
            for inline in options.inlines:
                inline = mixin_ella_admin(inline)
        admin.AdminSite.register = register_ella_admin(admin.AdminSite.register)


class EllaAdminOptionsMixin(object):
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'slug':
            return forms.RegexField('^[0-9a-z-]+$', max_length=255, **kwargs)
        if db_field.name == 'target_ct':
            kwargs['widget'] = widgets.ContentTypeWidget
        if db_field.name == 'target_id':
            kwargs['widget'] = widgets.ForeignKeyRawIdWidget
        if db_field.name == 'source_ct':
            kwargs['widget'] = widgets.ContentTypeWidget
        if db_field.name == 'source_id':
            kwargs['widget'] = widgets.ForeignKeyRawIdWidget
        return super(EllaAdminOptionsMixin, self).formfield_for_dbfield(db_field, **kwargs)


    def queryset(self, request):
        from ella.ellaadmin import models
        from django.db.models import Q
        q = admin.ModelAdmin.queryset(self, request)

        self.model._meta.get_field('category')
        perm = self.opts.app_label + '.' + self.opts.get_delete_permission()
        q = q.filter(
                Q(category__site__in=models.applicable_sites(request.user, perm)) |
                Q(category__in=models.applicable_categories(request.user, perm))
)

        return q

    def has_change_permission(self, request, obj):
        """
        Returns True if the given request has permission to change the given
        Django model instance.

        If `obj` is None, this should return True if the given request has
        permission to change *any* object of the given type.
        """
        if obj is None or not hasattr(obj, 'category'):
            return admin.ModelAdmin.has_change_permission(self, request, obj)
        opts = self.opts
        return models.has_permission(user, obj, obj.category, opts.get_change_permission())

class ExtendedModelAdmin(EllaAdminOptionsMixin, admin.ModelAdmin):
    pass

site = EllaAdminSite()

