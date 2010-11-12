# -*- coding: UTF-8 -*-
from django.contrib.contenttypes.models import ContentType
from django import template
from django.utils.encoding import smart_str
from django.utils.text import capfirst
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy, ugettext
from django.core.urlresolvers import reverse

from ella.newman import site, permission
from ella.newman.utils import get_log_entries
from ella.utils.text import cz_compare

from ella.newman.conf import newman_settings

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
    app_list.sort(
        lambda x, y: cz_compare(
            ugettext( x['name'] ),
            ugettext( y['name'] )
        )
    )

    # Sort the models alphabetically within each app.
    for app in app_list:
        app['models'].sort(lambda x, y: cz_compare(x['name'], y['name']))

    return {
        'NEWMAN_MEDIA_URL': context['NEWMAN_MEDIA_URL'],
        'app_list': app_list
    }


@register.inclusion_tag('newman/tpl_tags/newman_favorites.html', takes_context=True)
def newman_favorites(context):
    global_favs = []
    applications = newman_topmenu(context)['app_list']
    for model_name in newman_settings.FAVORITE_ITEMS:
        app_name, model_name = model_name.lower().split('.', 1)
        app = None
        for a in applications:
            if a['name'].lower() == app_name:
                app = a
                break
        if not app:
            continue
        model_found = None
        for m in app['models']:
            if m['model'] == model_name:
                model_found = m
                global_favs.append(m)
                break

    #global_favs.sort(lambda x, y: cz_compare(x['name'], y['name']))
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

class NewmanUrlNode(template.Node):
    " Resolves URL to kobayashi's url notation containing # char "
    newman_base_url = None

    def __init__(self, view_name, args, kwargs, as_var):
        self.view_name = view_name
        self.args = args
        self.kwargs = kwargs
        self.as_var = as_var
        if not NewmanUrlNode.newman_base_url:
            NewmanUrlNode.newman_base_url = reverse('newman:index')

    def render(self, context):
        kwargs = dict([(smart_str(k,'ascii'), v.resolve(context))
                       for k, v in self.kwargs.items()])
        url = reverse(self.view_name, args=self.args, kwargs=kwargs)
        final_url = url
        found = url.find(self.newman_base_url)
        if found > -1:
            position = found + len(self.newman_base_url)
            fragments = (
                self.newman_base_url,
                '#/',
                url[position:]
            )
            final_url = ''.join(fragments)

        if self.as_var:
            context[self.as_var] = final_url
            return ''
        return final_url

@register.tag
def newmanurl(parser, token):
    """
    Returns an absolute URL matching given Newman's view with its parameters.
    """
    bits = token.split_contents()
    if len(bits) < 2:
        raise template.TemplateSyntaxError("'%s' takes at least one argument"
                                  " (path to a view)" % bits[0])
    viewname = bits[1]
    args = []
    kwargs = {}
    asvar = None

    if len(bits) > 2:
        bits = iter(bits[2:])
        for bit in bits:
            if bit == 'as':
                asvar = bits.next()
                break
            else:
                for arg in bit.split(","):
                    if '=' in arg:
                        k, v = arg.split('=', 1)
                        k = k.strip()
                        kwargs[k] = parser.compile_filter(v)
                    elif arg:
                        args.append(parser.compile_filter(arg))
    return NewmanUrlNode(viewname, args, kwargs, asvar)


class GetNewmanUrlNode(template.Node):
    def __init__(self, object):
        self.object = object

    def render(self, context):
        obj = template.Variable(self.object).resolve(context)
        ct = ContentType.objects.get_for_model(obj.__class__)
        return "%s#/%s/%s/%s/" % (reverse('newman:index'), ct.app_label, ct.model, obj.pk)

@register.tag
def get_newman_url(parser, token):
    """
    Returns absolute newman admin url for object
    """

    bits = token.split_contents()

    if len(bits) != 3 or bits[1] != 'for':
        raise template.TemplateSyntaxError("{% get_newman_url for <object> %}")

    return GetNewmanUrlNode(bits[2])

class NewmanPdbNode(template.Node):
    def render(self, context):
        from django.conf import settings
        if settings.DEBUG:
            try:
                import ipdb;ipdb.set_trace()
            except ImportError:
                import pdb;pdb.set_trace()
        return ''

@register.tag
def newman_pdb(parser, token):
    return NewmanPdbNode()
