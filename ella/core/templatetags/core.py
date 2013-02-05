import logging

from django import template
from django.db import models
from django.utils.encoding import smart_str
from django.utils.safestring import mark_safe
from django.template.defaultfilters import stringfilter
from django.contrib.contenttypes.models import ContentType

from ella.core.models import Listing, Category
from ella.core.managers import ListingHandler
from ella.core.cache.utils import get_cached_object
from ella.core.box import Box


log = logging.getLogger('ella.core.templatetags')
register = template.Library()


class ListingNode(template.Node):
    def __init__(self, var_name, parameters):
        self.var_name = var_name
        self.parameters = parameters

    def render(self, context):
        params = {}
        for key, value in self.parameters.items():
            if isinstance(value, template.Variable):
                value = value.resolve(context)
            params[key] = value

        if 'category' in params and isinstance(params['category'], basestring):
            params['category'] = Category.objects.get_by_tree_path(params['category'])

        limits = {}
        if 'offset' in params:
            # templates are 1-based, compensate
            limits['offset'] = params.pop('offset') - 1

        if 'count' in params:
            limits['count'] = params.pop('count')

        lh = Listing.objects.get_queryset_wrapper(**params)

        context[self.var_name] = lh.get_listings(**limits)
        return ''


@register.tag
def listing(parser, token):
    """
    Tag that will obtain listing of top objects for a given category and store them in context under given name.

    Usage::

        {% listing <limit>[ from <offset>][of <app.model>[, <app.model>[, ...]]][ for <category> ] [with children|descendents] [using listing_handler] as <result> %}

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
        ``exclude``                         Variable including a ``Publishable`` to omit.
        ``using``                           Name of Listing Handler ro use
        ``result``                          Store the resulting list in context under given
                                            name.
        ==================================  ================================================

    Examples::

        {% listing 10 of articles.article for "home_page" as obj_list %}
        {% listing 10 of articles.article for category as obj_list %}
        {% listing 10 of articles.article for category with children as obj_list %}
        {% listing 10 of articles.article for category with descendents as obj_list %}
        {% listing 10 from 10 of articles.article as obj_list %}
        {% listing 10 of articles.article, photos.photo as obj_list %}

    """
    var_name, parameters = listing_parse(token.split_contents())
    return ListingNode(var_name, parameters)

LISTING_PARAMS = set(['of', 'for', 'from', 'as', 'using', 'with', 'without', ])

def listing_parse(input):
    params = {}
    if len(input) < 4:
        raise template.TemplateSyntaxError, "%r tag argument should have at least 4 arguments" % input[0]
    o = 1
    # limit
    params['count'] = template.Variable(input[o])
    o = 2

    params['category'] = Category.objects.get_by_tree_path('')
    while o < len(input):
        # offset
        if input[o] == 'from':
            params['offset'] = template.Variable(input[o + 1])
            o = o + 2

        # from - models definition
        elif input[o] == 'of':
            o = o + 1
            mods = []
            while input[o] not in LISTING_PARAMS:
                mods.append(input[o])
                o += 1

            l = []
            for mod in ''.join(mods).split(','):
                m = models.get_model(*mod.split('.'))
                if m is None:
                    raise template.TemplateSyntaxError, "%r tag cannot list objects of unknown model %r" % (input[0], mod)
                l.append(ContentType.objects.get_for_model(m))
            params['content_types'] = l

        # for - category definition
        elif input[o] == 'for':
            params['category'] = template.Variable(input[o + 1])
            o = o + 2

        # with
        elif input[o] == 'with':
            o = o + 1
            if input[o] == 'children':
                params['children'] = ListingHandler.IMMEDIATE
            elif input[o] == 'descendents':
                params['children'] = ListingHandler.ALL
            else:
                raise template.TemplateSyntaxError, "%r tag's argument 'with' required specification (with children|with descendents)" % input[0]
            o = o + 1

        # without (exclude publishable
        elif input[o] == 'without':
            params['exclude'] = template.Variable(input[o + 1])
            o = o + 2

        # using (isting handlers)
        elif input[o] == 'using':
            params['source'] = template.Variable(input[o + 1])
            o = o + 2

        # as
        elif input[o] == 'as':
            var_name = input[o + 1]
            o = o + 2
            break
        else:
            raise template.TemplateSyntaxError('Unknown param for %s: %r' % (input[0], input[o]))
    else:
        raise template.TemplateSyntaxError, "%r tag requires 'as' argument" % input[0]

    if o < len(input):
        raise template.TemplateSyntaxError, "%r tag requires 'as' as last argument" % input[0]

    return var_name, params

class EmptyNode(template.Node):
    def render(self, context):
        return u''

class ObjectNotFoundOrInvalid(Exception): pass

class BoxNode(template.Node):

    def __init__(self, box_type, nodelist, model=None, lookup=None, var=None):
        self.box_type, self.nodelist, self.var, self.lookup, self.model = box_type, nodelist, var, lookup, model

    def get_obj(self, context):
        if self.model and self.lookup:
            if isinstance(self.lookup[1], template.Variable):
                try:
                    lookup_val = self.lookup[1].resolve(context)
                except template.VariableDoesNotExist, e:
                    log.warning('BoxNode: Template variable does not exist. var_name=%s', self.lookup[1].var)
                    raise ObjectNotFoundOrInvalid()

            else:
                lookup_val = self.lookup[1]

            try:
                obj = get_cached_object(self.model, **{self.lookup[0] : lookup_val})
            except (models.ObjectDoesNotExist, AssertionError), e:
                log.warning('BoxNode: %s (%s : %s)', str(e), self.lookup[0], lookup_val)
                raise ObjectNotFoundOrInvalid()
        else:
            try:
                obj = self.var.resolve(context)
            except template.VariableDoesNotExist, e:
                log.warning('BoxNode: Template variable does not exist. var_name=%s', self.var.var)
                raise ObjectNotFoundOrInvalid()

            if not obj:
                raise ObjectNotFoundOrInvalid()
        return obj

    def render(self, context):

        try:
            obj = self.get_obj(context)
        except ObjectNotFoundOrInvalid:
            return ''

        box = getattr(obj, 'box_class', Box)(obj, self.box_type, self.nodelist)

        if not box or not box.obj:
            log.warning('BoxNode: Box does not exists.')
            return ''

        # render the box
        return box.render(context)

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
        return BoxNode(bits[1], nodelist, var=template.Variable(bits[3]))
    else:
        model = models.get_model(*bits[3].split('.'))
        if model is None:
            return EmptyNode()

        lookup_val = template.Variable(bits[6])
        try:
            lookup_val = lookup_val.resolve({})
        except template.VariableDoesNotExist:
            pass
        return BoxNode(bits[1], nodelist, model=model, lookup=(smart_str(bits[5]), lookup_val))

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
    Renders a rich-text field using defined markup.

    Example::

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

