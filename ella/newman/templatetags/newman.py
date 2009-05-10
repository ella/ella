from django import template
from django.utils.text import capfirst
from django.utils.safestring import mark_safe

from ella.newman import site, permission


register = template.Library()

@register.inclusion_tag('newman/tpl_tags/newman_topmenu.html', takes_context=True)
def newman_topmenu(context):
    app_dict = {}
    req = context['request']
    user = context['user']

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
                    'model': model.__name__.lower(),
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

    return {
        'NEWMAN_MEDIA_URL': context['NEWMAN_MEDIA_URL'],
        'app_list': app_list
    }


FAVS = (
    'publishable',
    'article',
    'placement',
    'photo',
    'gallerie',
    'poll',
    'position',
    'category',
    'author',
)

@register.inclusion_tag('newman/tpl_tags/newman_favorites.html', takes_context=True)
def newman_favorites(context):
    global_favs = []
    all_apps = newman_topmenu(context)
    for app in all_apps['app_list']:
        for m in app['models']:
            if m['model'] in FAVS:
                global_favs.append(m)

    return {
        'NEWMAN_MEDIA_URL': context['NEWMAN_MEDIA_URL'],
        'favs': global_favs
    }

def newman_list_filter(cl, spec):
    return {
        'title': spec.title(),
        'choices' : list(spec.choices(cl)),
        'spec': spec
    }
newman_list_filter = register.inclusion_tag('newman/tpl_tags/filter.html')(newman_list_filter)
