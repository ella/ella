from django import template
from django.utils.text import capfirst
from django.utils.safestring import mark_safe

from ella.newman import site, permission
from django.utils.translation import ugettext_lazy
from ella.newman.utils import get_log_entries


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
#    'placement',
    'photo',
    'gallery',
    'survey',
    'quiz',
    'contest',
    'interview',
    'position',
#    'category',
#    'author',
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

@register.simple_tag
def newman_contenttypes():
    out = []
    for ct in site.applicable_content_types:
        out.append('"%d": {"path": "/%s/%s/", "title": "%s"}' % (ct.pk, ct.app_label, ct.model, ugettext_lazy(ct.name)))
    return 'var AVAILABLE_CONTENT_TYPES = {%s};' % ", ".join(out)

class NewmanLogNode(template.Node):
    def __init__(self, limit, varname):
        self.limit, self.varname = limit, varname

    def render(self, context):
        user = context['user']
        params = {}
        if not user.is_superuser:
            params.update({'user': user})
        context[self.varname] = get_log_entries(limit=self.limit, filters=params)
        return ''

class NewmanLog():
    def __init__(self, tag_name):
        self.tag_name = tag_name

    def __call__(self, parser, token):
        tokens = token.contents.split()
        if len(tokens) < 4:
            raise template.TemplateSyntaxError, "'%s' statements require two arguments" % self.tag_name
        if not tokens[1].isdigit():
            raise template.TemplateSyntaxError, "First argument in '%s' must be an integer" % self.tag_name
        if tokens[2] != 'as':
            raise template.TemplateSyntaxError, "Second argument in '%s' must be 'as'" % self.tag_name
        return NewmanLogNode(limit=tokens[1], varname=tokens[3])

register.tag('newman_log', NewmanLog('newman_log'))
