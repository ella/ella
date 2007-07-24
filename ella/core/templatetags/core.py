from django import template
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured
from django.utils.encoding import smart_str

from ella.core.models import Listing
from ella.core.box import *

register = template.Library()

class ListingNode(template.Node):
    def __init__(self, var_name, parameters, parameters_to_resolve):
        self.var_name = var_name
        self.parameters = parameters
        self.parameters_to_resolve = parameters_to_resolve

    def render(self, context):
        for key in self.parameters_to_resolve:
            self.parameters[key] = template.resolve_variable(self.parameters[key], context)
        #if isinstance(self.parameters['category'], basestring):
        #    if  self.parameters['category'].isdigit() -- ID to lookup
        #    else: SLUG to lookup
        context[self.var_name] = Listing.objects.get_listing(**self.parameters)
        return ''

@register.tag
def listing(parser, token):
    """
    Tag that will obtain listing of top (priority-wise) objects for a given category and store them in context under given name.

    Usage::

        {% listing <limit>[ from <offset>][of <app.model>[, <app.model>[, ...]]][ for <category>][ with [immediate] subcategories] as <result> %}

    Parameters:

        ==================================  ================================================
        Option                              Description
        ==================================  ================================================
        ``limit``                           Number of objects to retrieve.
        ``from offset``                     Starting with number (1-based), starts from first
                                            if no offset specified.
        ``of app.model, ...``               List of allowed models, all if omitted.
        ``for category``                    Category of the listing, all categories if not
                                            specified. Can be either string (slug), digit (id)
                                            or variable containing a Category object.
        ``with [immediate] subcategories``  Include descendants of the specified category. If
                                            ``immediate`` specified, include just the direct
                                            children. Use just the category itself if not
                                            specified.
        ``as result``                       Store the resulting list in context under given
                                            name.
        ==================================  ================================================

    Examples::

        {% listing 10 of articles.article for "home_page" as obj_list %}
        {% listing 10 of articles.article for category with subcategories as obj_list %}
        {% listing 10 from 10 of articles.article as obj_list %}
        {% listing 10 of articles.article, photos.photo for 1 as obj_list %}
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
            params['children'] = Listing.obects.ALL
        else:
            raise templpate.TemplateSyntaxError, "%r tag's argument 'with' required specification (with children|with descendents)" % input[0]
        o=o+1
    # as
    if input[o] == 'as':
        var_name = input[o+1]
    else:
        raise template.TemplateSyntaxError, "%r tag requires 'as' argument" % input[0]

    return var_name, params, params_to_resolve



def parse_params(params):
    lines = params.split('\n')
    # TODO: handle syntax errors (lines without ':')
    return dict((key.strip(), value.strip()) for key, value in map(lambda x: x.split(':', 1), lines))

class BoxNode(template.Node):
    def __init__(self, obj, box_type, nodelist):
        self.obj, self.box_type, self.nodelist = obj, box_type, nodelist

    def render(self, context):
        if isinstance(self.obj, basestring):
            obj = template.resolve_variable(self.obj, context)
        else:
            obj = self.obj

        if hasattr(obj, 'Box'):
            box = obj.Box(self.box_type, self.nodelist)
        else:
            box = Box(obj, self.box_type, self.nodelist)

        # push context stack
        context.push()
        # render the box itself
        box.prepare(context)
        # set the name of this box so that its children can pick up the dependencies
        box_key = box.get_cache_key()
        context[BOX_INFO] = (obj, box_key)
        # render the box
        result = box.render()
        # restore the context
        context.pop()

        if BOX_INFO in context:
            # record dependecies
            Dependency.objects.get_or_create(obj, box_key, *context[BOX_INFO])
        return result

@register.tag('box')
def do_box(parser, token):
    """
    Tag Node representing our idea of a reusable box. It can handle multiple paramters in its body, that can
    contain other django template. The boxing facility keeps track of box dependencies which allows it to invalidate
    the cache of a parent box when the box itself is being invalidated.

    The object is passed in context as ``object`` when rendering the box parameters.

    Usage::

        {% box BOXTYPE for APP_LABEL.MODEL_NAME with FIELD VALUE %}
        {% box BOXTYPE for var_name %}

    Examples::

        {% box home_listing for articles.article with slug "some-slug" %}{% endbox %}

        {% box home_listing for articles.article with pk object_id %}
            template_name : {{object.get_box_template}}
        {% endbox %}

        {% box home_listing for article %}{% endbox %}
    """
    bits = token.split_contents()


    # {% box BOXTYPE for var_name %}                {% box BOXTYPE for content.type with PK_FIELD PK_VALUE %}
    if (len(bits) != 4 or bits[2] != 'for') and (len(bits) != 7 or bits[2] != 'for' or bits[4] != 'with'):
        raise template.TemplateSyntaxError, "{% box BOXTYPE for content.type with FIELD VALUE %} or {% box BOXTYPE for var_name %}"

    if len(bits) == 4:
        # var_name
        obj = bits[3]
    else:
        model = models.get_model(*bits[3].split('.'))
        if model is None:
            raise template.TemplateSyntaxError, "Model %r does not exist" % bits[3]
        ct = ContentType.objects.get_for_model(model)

        try:
            obj = ct.get_object_for_this_type(**{smart_str(bits[5]) : bits[6]})
        except models.ObjectDoesNotExist:
            raise template.TemplateSyntaxError, "Model %r with field %r equal to %r does not exist." % (bits[3], bits[5], bits[6])
        except AssertionError:
            raise template.TemplateSyntaxError, "Model %r with field %r equal to %r does not refer to a single object." % (bits[3], bits[5], bits[6])

    nodelist = parser.parse(('end' + bits[0],))
    parser.delete_first_token()

    return BoxNode(obj, bits[1], nodelist)

@register.inclusion_tag('core/box_media.html', takes_context=True)
def box_media(context):
    return {'media' : context.dicts[-1].get(MEDIA_KEY, None)}

