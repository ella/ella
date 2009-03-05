from django import template
from django.utils.safestring import mark_safe

from ella.newman import site, permission

register = template.Library()

class AdminApplistNode(template.Node):
    def __init__(self, varname):
        self.varname = varname

    def render(self, context):
        req = context['request']
        from django.utils.text import capfirst
        app_dict = {}
        user = req.user

        for model, model_admin in site._registry.items():
            app_label = model._meta.app_label
            has_module_perms = user.has_module_perms(app_label) or permission.has_model_list_permission(user, model)

            if has_module_perms:
                perms = {
                    'add': model_admin.has_add_permission(req),
                    'change': model_admin.has_change_permission(req),
                    'delete': model_admin.has_delete_permission(req),
}

                # Check whether user has any perm for this module.
                # If so, add the module to the model_list.
                if True in perms.values():
                    model_dict = {
                        'name': capfirst(model._meta.verbose_name_plural),
                        'admin_url': mark_safe('%s/%s/' % (app_label, model.__name__.lower())),
                        'perms': perms,
}
                    if app_label in app_dict:
                        app_dict[app_label]['models'].append(model_dict)
                    else:
                        app_dict[app_label] = {
                            'name': app_label.title(),
                            'has_module_perms': has_module_perms,
                            'models': [model_dict],
}

        # Sort the apps alphabetically.
        app_list = app_dict.values()
        app_list.sort(lambda x, y: cmp(x['name'], y['name']))

        # Sort the models alphabetically within each app.
        for app in app_list:
            app['models'].sort(lambda x, y: cmp(x['name'], y['name']))

        context[self.varname] = app_list
        return ''

@register.tag
def get_admin_app_list(parser, token):
    """
    Returns a list of installed applications and models for which the current user
    has at least one permission.

    Syntax::

        {% get_admin_app_list as [context_var_containing_app_list] %}

    Example usage::

        {% get_admin_app_list as admin_app_list %}
    """
    tokens = token.contents.split()
    if len(tokens) < 3:
        raise template.TemplateSyntaxError, "'%s' tag requires two arguments" % tokens[0]
    if tokens[1] != 'as':
        raise template.TemplateSyntaxError, "First argument to '%s' tag must be 'as'" % tokens[0]
    return AdminApplistNode(tokens[2])
