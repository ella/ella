import logging

from django.conf import settings
from django import template
from django.db import models
from django.utils.encoding import smart_str
from django.utils.safestring import mark_safe
from django.template.defaultfilters import stringfilter

from ella.core.models import Listing, Category
from ella.core.cache.utils import get_cached_object
from ella.core.cache.invalidate import CACHE_DELETER
from ella.core.box import Box
from ella.core.conf import core_settings


log = logging.getLogger('ella.core.templatetags')
register = template.Library()

class ListingNode(template.Node):
    def __init__(self, var_name, parameters, parameters_to_resolve):
        self.var_name = var_name
        self.parameters = parameters
        self.parameters_to_resolve = parameters_to_resolve
        self.resolved_parameters = self.parameters.copy()

    def resolve_parameter(self, key, context):
        value = self.parameters[key]
        if key == 'count':
            if type(value) in (str, unicode) and value.isdigit():
                return int(value)
        return template.Variable(value).resolve(context)

    def render(self, context):
        unique_var_name = None
        for key in self.parameters_to_resolve:
            if key == 'unique':
                unique_var_name = self.parameters[key]
            if key == 'unique' and unique_var_name not in context.dicts[-1]: # autocreate variable in context
                self.resolved_parameters[key] = context.dicts[-1][ unique_var_name ] = set()
                continue
            #self.parameters[key] = template.Variable(self.parameters[key]).resolve(context)
            self.resolved_parameters[key] = self.resolve_parameter(key, context)
        if self.resolved_parameters.has_key('category') and \
            isinstance(self.resolved_parameters['category'], basestring):
            self.resolved_parameters['category'] = get_cached_object(Category, tree_path=self.resolved_parameters['category'], site__id=settings.SITE_ID)
        out = Listing.objects.get_listing(**self.resolved_parameters)

        if 'unique' in self.parameters:
            unique = self.resolved_parameters['unique'] #context[unique_var_name]
            map(lambda x: unique.add(x.placement_id),out)
        context[self.var_name] = out
        return ''

@register.tag
def listing(parser, token):
    """
    Tag that will obtain listing of top (priority-wise) objects for a given category and store them in context under given name.

    Usage::

        {% listing <limit>[ from <offset>][of <app.model>[, <app.model>[, ...]]][ for <category> ] [with children|descendents] as <result> [unique [unique_set_name]] %}

    Parameters:

        ==================================  ================================================
        Option                              Description
        ==================================  ================================================
        ``limit``                           Number of objects to retrieve.
        ``offset``                          Starting with number (1-based), starts from first
                                            if no offset specified.
        ``app.model``, ...                  List of allowed models, all if omitted.
        ``category``                        Category of the listing, all categories if not
                                            specified. Can be either string (tree path),
                                            or variable containing a Category object.
        ``children``                        Include items from direct subcategories.
        ``descendents``                     Include items from all descend subcategories.
        ``result``                          Store the resulting list in context under given
                                            name.
        ``unique``                          Unique items across multiple listings.
        ``unique_set_name``                 Name of context variable used to hold the data is optional.
        ==================================  ================================================

    Examples::

        {% listing 10 of articles.article for "home_page" as obj_list %}
        {% listing 10 of articles.article for category as obj_list %}
        {% listing 10 of articles.article for category with children as obj_list %}
        {% listing 10 of articles.article for category with descendents as obj_list %}
        {% listing 10 from 10 of articles.article as obj_list %}
        {% listing 10 of articles.article, photos.photo as obj_list %}

        Unique items across multiple listnings::
        {% listing 10 for category_uno as obj_list unique %}
        {% listing 4 for category_duo as obj_list unique %}
        {% listing 10 for category_uno as obj_list unique unique_set_name %}
        {% listing 4 for category_duo as obj_list unique unique_set_name %}
    """
    var_name, parameters, parameters_to_resolve = listing_parse(token.split_contents())
    return ListingNode(var_name, parameters, parameters_to_resolve)

def listing_parse(input):
    params={}
    params_to_resolve=[]
    if len(input) < 4:
        raise template.TemplateSyntaxError, "%r tag argument should have at least 4 arguments" % input[0]
    o=1
    # limit
    params['count'] = input[o]
    params_to_resolve.append('count')
    o=2
    # offset
    if input[o] == 'from':
        params['offset'] = input[o+1]
        params_to_resolve.append('offset')
        o=o+2
    # from - models definition
    if input[o] == 'of':
        o=o+1
        if 'for' in input:
            mc = input.index('for')
        elif 'as' in input:
            mc = input.index('as')
        if mc > 0:
            l = []
            for mod in ''.join(input[o:mc]).split(','):
                m = models.get_model(*mod.split('.'))
                if m is None:
                    raise template.TemplateSyntaxError, "%r tag cannot list objects of unknown model %r" % (input[0], mod)
                l.append(m)
            params['mods'] = l
        o=mc
    # for - category definition
    if input[o] == 'for':
        params['category'] = input[o+1]
        params_to_resolve.append('category')
        o=o+2
    # with
    if input[o] == 'with':
        o=o+1
        if input[o] == 'children':
            params['children'] = Listing.objects.IMMEDIATE
        elif input[o] == 'descendents':
            params['children'] = Listing.objects.ALL
        else:
            raise template.TemplateSyntaxError, "%r tag's argument 'with' required specification (with children|with descendents)" % input[0]
        o=o+1

    # as
    if input[o] == 'as':
        var_name = input[o+1]
    else:
        raise template.TemplateSyntaxError, "%r tag requires 'as' argument" % input[0]

    # unique
    if input[-2].lower() == 'unique':
        params['unique'] = input[-1]
        params_to_resolve.append('unique')
    elif input[-1].lower() == 'unique':
        params['unique'] = core_settings.LISTING_UNIQUE_DEFAULT_SET
        params_to_resolve.append('unique')

    return var_name, params, params_to_resolve

class EmptyNode(template.Node):
    def render(self, context):
        return u''

class ObjectNotFoundOrInvalid(Exception): pass

class BoxNode(template.Node):

    def __init__(self, box_type, nodelist, model=None, lookup=None, var_name=None):
        self.box_type, self.nodelist, self.var_name, self.lookup, self.model = box_type, nodelist, var_name, lookup, model

    def get_obj(self, context=None):
        if self.model and self.lookup:
            if context:
                try:
                    lookup_val = template.Variable(self.lookup[1]).resolve(context)
                except template.VariableDoesNotExist:
                    lookup_val = self.lookup[1]
            else:
                lookup_val = self.lookup[1]

            try:
                obj = get_cached_object(self.model, **{self.lookup[0] : lookup_val})
            except models.ObjectDoesNotExist, e:
                log.error('BoxNode: %s (%s : %s)' % (str(e), self.lookup[0], lookup_val))
                raise ObjectNotFoundOrInvalid()
            except AssertionError, e:
                log.error('BoxNode: %s (%s : %s)' % (str(e), self.lookup[0], lookup_val))
                raise ObjectNotFoundOrInvalid()
        else:
            if not context:
                raise ObjectNotFoundOrInvalid()
            try:
                obj = template.Variable(self.var_name).resolve(context)
            except template.VariableDoesNotExist, e:
                log.error('BoxNode: Template variable does not exist. var_name=%s' % self.var_name)
                raise ObjectNotFoundOrInvalid()
            if not obj:
                raise ObjectNotFoundOrInvalid()
        return obj

    def render(self, context):

        try:
            obj = self.get_obj(context)
        except ObjectNotFoundOrInvalid, e:
            return ''

        box = getattr(obj, 'box_class', Box)(obj, self.box_type, self.nodelist)

        if not box or not box.obj:
            log.warning('BoxNode: Box does not exists.')
            return ''

        # render the box itself
        box.prepare(context)
        # set the name of this box so that its children can pick up the dependencies
        box_key = box.get_cache_key()

        # push context stack
        context.push()
        context[core_settings.BOX_INFO] = box_key

        # render the box
        result = box.render()
        # restore the context
        context.pop()

        # record parent box dependecy on child box or cached full-page on box
        if not (core_settings.DOUBLE_RENDER and box.can_double_render) and (core_settings.BOX_INFO in context or core_settings.ECACHE_INFO in context):
            if core_settings.BOX_INFO in context:
                source_key = context[core_settings.BOX_INFO]
            elif core_settings.ECACHE_INFO in context:
                source_key = context[core_settings.ECACHE_INFO]
            CACHE_DELETER.register_dependency(source_key, box_key)

        return result

@register.tag('box')
def do_box(parser, token):
    """
    Tag Node representing our idea of a reusable box. It can handle multiple
    parameters in its body which will then be accessible via ``{{ box.params
    }}`` in the template being rendered.

    .. note::
        The inside of the box will be rendered only when redering the box in
        current context and the ``object`` template variable will be present
        and set to the target of the box.

    Author of any ``Model`` can specify it's own ``box_class`` which enables
    custom handling of some content types (boxes for polls for example need
    some extra information to render properly).

    Boxes, same as :ref:`core-views`, look for most specific template for a given
    object an only fall back to more generic template if the more specific one
    doesn't exist. The list of templates it looks for:

    * ``box/category/<tree_path>/content_type/<app>.<model>/<slug>/<box_name>.html``
    * ``box/category/<tree_path>/content_type/<app>.<model>/<box_name>.html``
    * ``box/category/<tree_path>/content_type/<app>.<model>/box.html``
    * ``box/content_type/<app>.<model>/<slug>/<box_name>.html``
    * ``box/content_type/<app>.<model>/<box_name>.html``
    * ``box/content_type/<app>.<model>/box.html``
    * ``box/<box_name>.html``
    * ``box/box.html``

    .. note::
        Since boxes work for all models (and not just ``Publishable`` subclasses),
        some template names don't exist for some model classes, for example
        ``Photo`` model doesn't have a link to ``Category`` so that cannot be used.

    Boxes are always rendered in current context with added variables:

    * ``object`` - object being represented
    * ``box`` - instance of ``ella.core.box.Box``

    Usage::

        {% box <boxtype> for <app.model> with <field> <value> %}
            param_name: value
            param_name_2: {{ some_var }}
        {% endbox %}

        {% box <boxtype> for <var_name> %}
            ...
        {% endbox %}

    Parameters:

        ==================================  ================================================
        Option                              Description
        ==================================  ================================================
        ``boxtype``                         Name of the box to use
        ``app.model``                       Model class to use
        ``field``                           Field on which to do DB lookup
        ``value``                           Value for DB lookup
        ``var_name``                        Template variable to get the instance from
        ==================================  ================================================

    Examples::

        {% box home_listing for articles.article with slug "some-slug" %}{% endbox %}

        {% box home_listing for articles.article with pk object_id %}
            template_name : {{object.get_box_template}}
        {% endbox %}

        {% box home_listing for article %}{% endbox %}
    """
    bits = token.split_contents()

    nodelist = parser.parse(('end' + bits[0],))
    parser.delete_first_token()
    return _parse_box(nodelist, bits)

def _parse_box(nodelist, bits):
    # {% box BOXTYPE for var_name %}                {% box BOXTYPE for content.type with PK_FIELD PK_VALUE %}
    if (len(bits) != 4 or bits[2] != 'for') and (len(bits) != 7 or bits[2] != 'for' or bits[4] != 'with'):
        raise template.TemplateSyntaxError, "{% box BOXTYPE for content.type with FIELD VALUE %} or {% box BOXTYPE for var_name %}"

    if len(bits) == 4:
        # var_name
        return BoxNode(bits[1], nodelist, var_name=bits[3])
    else:
        model = models.get_model(*bits[3].split('.'))
        if model is None:
            return EmptyNode()

        return BoxNode(bits[1], nodelist, model=model, lookup=(smart_str(bits[5]), bits[6]))

class RenderNode(template.Node):
    def __init__(self, var):
        self.var = template.Variable(var)

    def render(self, context):
        try:
            text = self.var.resolve(context)
        except template.VariableDoesNotExist:
            return ''

        template_name = 'render-%s' % self.var
        return template.Template(text, name=template_name).render(context)

@register.tag('render')
def do_render(parser, token):
    """
    {% render some_var %}
    """
    bits = token.split_contents()

    if len(bits) != 2:
        raise template.TemplateSyntaxError()

    return RenderNode(bits[1])

@register.filter
@stringfilter
def ipblur(text): # brutalizer ;-)
    """ blurs IP address  """
    import re
    m = re.match(r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.)\d{1,3}.*', text)
    if not m:
        return text
    return '%sxxx' % m.group(1)

@register.filter
@stringfilter
def emailblur(email):
    "Obfuscates e-mail addresses - only @ and dot"
    return mark_safe(email.replace('@', '&#64;').replace('.', '&#46;'))

