import logging

from django import template
from django.core.exceptions import ObjectDoesNotExist
from ella.core.models import Listing
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.encoding import smart_str
from django.template import TemplateSyntaxError, Variable
from django.conf import settings

from ella.utils.templatetags import parse_getforas_triplet
from ella.menu.models import Menu, MenuItem
from ella.core.cache.template_loader import select_template
from ella.core.models import Category


register = template.Library()
MENU_TPL_VAR = 'menu_var' # template variable name
log = logging.getLogger('ella.menu')


def highlight_items(context, menu_items, obj):
    howto = """
    core/views.py object_detail, creates context like that:
     context = {
            'placement' : placement,
            'object' : obj,
            'category' : cat,
            'content_type_name' : content_type,
            'content_type' : ct,
}
    core/views.py  home, context contains 'category' only
    core/views.py  category_detail,  context contains 'category' only
    """
    #TODO highlight by url
    def process_highlight(ct, obj_pk):
        for i in out:
            if i.target_ct == ct and i.target_id == obj_pk:
                setattr(i, 'selected_item', 'blabla')
                break
            children = MenuItem.objects.filter(parent=i, target_ct=ct, target_id=obj_pk)
            if children:
                setattr(i, 'selected_item', 'child')
                break

    out = menu_items.all()
    if 'content_type' in context and 'object' in context:
        process_highlight(context['content_type'], context['object'].pk)
    elif 'category' in context:
        ct = ContentType.objects.get_for_model(Category)
        process_highlight(ct, context['category'].pk)
    return out

#TODO @cache_this
def render_common(context, menu, obj, level=None):
    if not level:
        mi = MenuItem.objects.get_level(menu, 1, obj)
    else:
        mi = MenuItem.objects.get_level(menu, int(level), obj)
    #mih = highlight_items(context, mi, obj)
    context[MENU_TPL_VAR] = mi
    tpl = select_template(get_template_list(menu, obj))
    t = template.loader.get_template(tpl.name)
    return t.render(context)

class MenuForSpecificObjectNode(template.Node):
    def __init__(self, bits, level=None):
        self.level = level
        self.menu_slug = bits[1]
        if level:
            self.model_name = bits[5]
            self.model_field_names = map(lambda x: str(x), bits[7::2])
            self.model_field_values = bits[8::2]
        else:
            self.model_name = bits[3]
            self.model_field_names = map(lambda x: str(x), bits[5::2])
            self.model_field_values = bits[6::2]

    def render(self, context):
        if self.model_name.lower() != 'category':
            raise TemplateSyntaxError('{% menu %} tag supports only category content type at the moment.')
        kw = dict(zip(self.model_field_names, self.model_field_values))
        cats = Category.objects.filter(**kw)
        if not cats:
            log.warning('There are no Category instances returned by filter(%s)' % kw)
            return ''
        cat = cats[0]
        menus = Menu.objects.filter(slug=self.menu_slug, site=settings.SITE_ID)
        if not menus:
            log.warning('There are no Menu instances named "%s" for category %s' % (self.menu_slug, cat))
            return ''
        return render_common(context, menus[0], cat, self.level)

class MenuForObjectNode(template.Node):
    def __init__(self, bits, level=None):
        self.level = level
        self.menu_slug = bits[1]
        if level:
            self.object = bits[5]
        else:
            self.object = bits[3]

    def render(self, context):
        self.object = Variable(self.object).resolve(context)
        if not isinstance(self.object, Category):
            raise TemplateSyntaxError('Object should be instance of Category class. type is %s' % type(self.object))
        menus = Menu.objects.filter(slug=self.menu_slug, site=settings.SITE_ID)
        if not menus:
            log.warning('There are no Menu instances named "%s" for object %s' % (self.menu_slug, self.object))
            return ''
        return render_common(context, menus[0], self.object, self.level)

class MenuSimpleNode(template.Node):
    def __init__(self, menu_slug, level=None):
        self.menu_slug = menu_slug
        self.level = level

    def render(self, context):
        menus = Menu.objects.filter(slug=self.menu_slug, site=settings.SITE_ID)
        if not menus:
            log.warning('There are no Menu instances named "%s"' % self.menu_slug)
            return ''
        return render_common(context, menus[0], None, self.level)

def get_template_list(menu, target):
    prefix = 'inclusion_tags/menu'
    templates = []
    app_label = model_label = cat = None
    name = '%s.html' % menu.slug
    if not target:
        templates.append('%s/%s' % (prefix, name))
    if isinstance(target, Category):
        path = '%s/%s' % (name, target.path)
        cat = target
        templates.append('%s/category/%s/%s' % (prefix, cat.path, name))
        #iterate over category parents and add their template paths to templates list
        c = cat
        while c.tree_parent:
            c = c.tree_parent
            templates.append('%s/category/%s/%s' % (prefix, c.path, name))
        templates.append('%s/%s' % (prefix, name))
    elif hasattr(target, 'category'):
        cat = target.category
        if hasattr(target, '_meta'):
            app_label = target._meta.app_label
            model_label = target._meta.module_name
            if hasattr(target, 'slug'):
                templates.append('%s/category/%s/content_type/%s.%s/%s/%s' % (prefix, cat.path, app_label, model_label, target.slug, name))
            templates.append('%s/category/%s/content_type/%s.%s/%s' % (prefix, cat.path, app_label, model_label, name))
    elif issubclass(target.__class__, models.Model):
        app_label = target._meta.app_label
        model_label = target._meta.module_name
        templates.append('%s/content_type/%s.%s/%s' % (prefix, app_label, model_label, name))
    #return get_templates('menu.html', slug=menu.slug, category=cat, app_label=app_label, model_label=model_label)
    templates.append('%s/menu.html' % prefix)
    return templates


@register.tag
def menu(parser, token):
    """
    Get threads sorted by date of newest posts within each thread.

    Syntax::

        {% menu MENU_NAME [ level all | level 1 | level +1 ] [ for (APPLICATION.MODEL with FIELD VALUE | OBJECT) ]  %}

    Example usage::

        {% menu horizontal_menu [ level all | level 1 ] %}       # constructs horizontal menu
        {% menu mainmenu [ level all | level 1 ] for category with slug "zena"  %}
        {% menu mainmenu [ level all | level 1 ] for articles.article with pk 21 slug blabla field value %}
        {% menu mainmenu [ level all | level 1 ] for articles.article with pk obj.pk  %}
        {% menu mainmenu [ level all | level 1 ] for object  %}  # object is template variable containing model instance, i.e. Category instance
    """
    bits = token.split_contents()
    if 'level' in bits[:3]: # optional parameters - menu level
        level = bits[3]
        if len(bits) == 4:
            return MenuSimpleNode(bits[1], level)
        elif len(bits) == 6: # {% menu MENU_NAME level all for OBJECT %}
            return MenuForObjectNode(bits, level)
        elif len(bits) >= 9: # {% menu MENU_NAME level all for APPLICATION.MODEL with FIELD VALUE ... FIELDn VALUEn %}
            return MenuForSpecificObjectNode(bits, level)
    else: # optional level parameters not typed in
        if len(bits) == 2:
            return MenuSimpleNode(bits[1])
        elif len(bits) == 4: # {% menu MENU_NAME for OBJECT %}
            return MenuForObjectNode(bits)
        elif len(bits) >= 7: # {% menu MENU_NAME  for APPLICATION.MODEL with FIELD VALUE ... FIELDn VALUEn %}
            return MenuForSpecificObjectNode(bits)
    raise TemplateSyntaxError('Bad syntax in menu tag')
