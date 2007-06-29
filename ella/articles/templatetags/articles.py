import string
from django import template
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured

from nc.articles.models import Listing

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

@register.tag()
def listing(parser, token):
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
            params['children'] = 1
        elif input[o] == 'descendents':
            params['children'] = 2
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
        if isinstance(self.obj, basestring)
            obj = template.resolve_variable(self.obj)
        else:
            obj = self.obj

        if not hasattr(obj, 'Box'):
            # TODO: log error
            return ''

        box = obj.Box(self.box_type, self.nodelist)
        # push context stack
        context.push()
        # render the box itself
        box.prepare(context)
        # set the name of this box so that its children can pick up the dependencies
        box_key = box.get_key()
        context[BOX_INFO] = (obj, box_key)
        # render the box
        result = box.render()
        # restore the context
        context.pop()

        if BOX_INFO in context:
            # record dependecies
            Dependency.objects.get_or_create(obj, box_key, *context[BOX_INFO],)
        return result

@register.tag('box')
def do_box(parser, token):
    """
    Tag Node representing our idea of a reusable box. It can handle multiple paramters in its body, that can
    contain other django template. The boxing facility keeps track of box dependencies and allows them to
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
            obj = ct.get_object_for_this_type(**{bits[5] : bits[6]})
        except models.ObjectDoesNotExist:
            raise template.TemplateSyntaxError, "Model %r with field %r equal to %r does not exist." % (bits[3], bits[5], bits[6])
        except AssertionError:
            raise template.TemplateSyntaxError, "Model %r with field %r equal to %r does not refer to a single object." % (bits[3], bits[5], bits[6])

        if not hasattr(obj, 'Box'):
            raise template.TemplateSyntaxError, "Given object doesn't support Boxing."

    nodelist = parser.parse(('end' + bits[0],))

    return BoxNode(obj, bits[1], nodelist)

