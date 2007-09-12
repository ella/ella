from django.conf import settings
from django import template
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured
from django.utils.encoding import smart_str, force_unicode

from ella.core.models import Listing, Dependency, Related
from ella.core.box import *
from ella.core.cache.utils import get_cached_object

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

        {% listing <limit>[ from <offset>][of <app.model>[, <app.model>[, ...]]][ for <category>] as <result> %}

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
        ``as result``                       Store the resulting list in context under given
                                            name.
        ==================================  ================================================

    Examples::

        {% listing 10 of articles.article for "home_page" as obj_list %}
        {% listing 10 of articles.article for category as obj_list %}
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
    # as
    if input[o] == 'as':
        var_name = input[o+1]
    else:
        raise template.TemplateSyntaxError, "%r tag requires 'as' argument" % input[0]

    return var_name, params, params_to_resolve

class EmptyNode(template.Node):
    def render(self, context):
        return u''

class BoxNode(template.Node):
    def __init__(self, box_type, nodelist, model=None, lookup=None, var_name=None):
        self.box_type, self.nodelist, self.var_name, self.lookup, self.model = box_type, nodelist, var_name, lookup, model


    def render(self, context):
        if self.model and self.lookup:
            try:
                lookup_val = template.resolve_variable(self.lookup[1], context)
            except template.VariableDoesNotExist:
                lookup_val = self.lookup[1]

            try:
                obj = get_cached_object(self.model, **{self.lookup[0] : lookup_val})
            except models.ObjectDoesNotExist:
                return ''
            except AssertionError:
                return ''
        else:
            try:
                obj = template.resolve_variable(self.var_name, context)
            except template.VariableDoesNotExist:
                return ''

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
            source, source_key = context[BOX_INFO]
            Dependency.objects.report_dependency(source, source_key, obj, box_key)
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

    nodelist = parser.parse(('end' + bits[0],))
    parser.delete_first_token()

    # {% box BOXTYPE for var_name %}                {% box BOXTYPE for content.type with PK_FIELD PK_VALUE %}
    if (len(bits) != 4 or bits[2] != 'for') and (len(bits) != 7 or bits[2] != 'for' or bits[4] != 'with'):
        raise template.TemplateSyntaxError, "{% box BOXTYPE for content.type with FIELD VALUE %} or {% box BOXTYPE for var_name %}"

    if len(bits) == 4:
        # var_name
        return BoxNode(bits[1], nodelist, var_name=bits[3])
    else:
        model = models.get_model(*bits[3].split('.'))
        if model is None:
            if settings.DEBUG:
                raise template.TemplateSyntaxError, "Model %r does not exist" % bits[3]
            return EmptyNode()

        return BoxNode(bits[1], nodelist, model=model, lookup=(smart_str(bits[5]), bits[6]))

@register.inclusion_tag('core/box_media.html', takes_context=True)
def box_media(context):
    return {'media' : context.dicts[-1].get(MEDIA_KEY, None)}

class StaticBoxNode(template.Node):
    def __init__(self, box_type, level):
        self.box_type, self.level = box_type, level

    def render(self, context):
        if self.level:
            try:
                level = template.resolve_variable(self.level, context)
            except template.VariableDoesNotExist:
                level = 1
        else:
            level = 1

        context.push()
        context['level'] = level
        context['next_level'] = level + 1
        t = loader.get_template('box/static/%s.html' % self.box_type)
        resp = t.render(context)
        context.pop()
        return resp


@register.tag('staticbox')
def do_static_box(parser, token):
    """
    Include a static box (a simple template) with ``level`` and ``next_level`` variables in context.
    If no ``LEVEL`` paramter is specified, defaults to 1 (2 for ``next_level``).

    Usage::

        {% staticbox BOXTYPE %}
        {% staticbox BOXTYPE LEVEL %}

    Examples::

        {% staticbox home_listing %}

        {% staticbox home_listing 1 %}

        {% staticbox home_listing level %}

    """
    bits = token.split_contents()

    if  2 > len(bits) > 3:
        raise template.TemplateSyntaxError, '{% staticbox BOX_TYPE [LEVEL] %}'

    if len(bits) == 3:
        level = bits[2]
    else:
        level = None

    return StaticBoxNode(bits[1], level)

@register.inclusion_tag('core/box_media.html', takes_context=True)
def box_media(context):
    return {'media' : context.dicts[-1].get(MEDIA_KEY, None)}

@register.filter
def render(object, content_path):
    """
    A markdown filter that handles the rendering of any text containing markdown markup and/or django template tags.
    Only ``{{object}}`` and ``{{MEDIA_URL}}`` are available in the context.

    Usage::

        {{object|render:"property.to.render"}}

    Examples::

        {{article|render:"perex"}}
        {{article|render:"content.content"}}
    """
    import markdown
    from django.conf import settings
    path = content_path.split('.')
    content = object
    for step in path:
        try:
            content = getattr(content, step)
        except:
            raise template.TemplateSyntaxError, "Error accessing %r property of object %r" % (content_path, object)

    result = force_unicode(markdown.markdown(smart_str(content)))
    t = template.Template(result)
    return t.render(template.Context({'object' : object, 'MEDIA_URL' : settings.MEDIA_URL}))


class RelatedNode(template.Node):
    def __init__(self, obj_var, count, var_name, models=[]):
        self.obj_var, self.count, self.var_name, self.models = obj_var, count, var_name, models

    def render(self, context):
        try:
            obj = template.resolve_variable(self.obj_var, context)
        except template.VariableDoesNotExist:
            return ''

        related = []
        count = self.count

        # manually entered dependencies
        for rel in Related.objects.filter(source_ct=ContentType.objects.get_for_model(obj), source_id=obj._get_pk_val()):
            related.append(rel)
            count -= 1
            if count <= 0:
                break

        # related objects vie tags
        if self.models and count > 0:
            from tagging.models import TaggedItem
            for m in self.models:
                to_add = TaggedItem.objects.get_related(self.obj, m, count)
                for rel in to_add:
                    if rel != obj and rel not in related:
                        count -= 1
                        related.append(rel)
                    if count <= 0:
                        break

        # top objects in given category
        if count > 0:
            listings = Listing.objects.get_listing(category=obj.category, count=count, mods=self.models)
            related.extend(listing.target for listing in listings if listing.target != obj)

        context[self.var_name] = related
        return ''

@register.tag('related')
def do_related(parser, token):
    """
    {% related N [app_label.Model, ...] for object as var_name %}
    """
    bits = token.split_contents()

    if len(bits) < 6:
        raise template.TemplateSyntaxError, "{% related N [app_label.Model, ...] for object as var_name %}"

    if not bits[1].isdigit():
        raise template.TemplateSyntaxError, "Count must be an integer."

    if bits[-2] != 'as':
        raise template.TemplateSyntaxError, "Tag must end with as var_name "
    if bits[-4] != 'for':
        raise template.TemplateSyntaxError, "Tag must end with for object as var_name "

    mods = []
    for m in bits[2:-5]:
        if m == ',':
            continue
        if ',' in m:
            ms = m.split()
            for msm in ms:
                try:
                    mods.append(models.get_model(*msm.split('.')))
                except:
                    raise template.TemplateSyntaxError, "%r doesn't represent any model." % msm
        else:
            try:
                mods.append(models.get_model(*m.split('.')))
            except:
                raise template.TemplateSyntaxError, "%r doesn't represent any model." % m
    return RelatedNode(bits[-3], int(bits[1]), bits[-1], mods)






class ContainerNode(template.Node):
    def __init__(self, nodelist, parameters):
        self.nodelist = nodelist
        self.params = parameters

    def render(self, context):
        context.push()

        for key, value in self.params.items():
            try:
                context[key] = template.resolve_variable(value, context)
            except template.VariableDoesNotExist:
                context[key] = value

        if 'level' in context:
            try:
                context['next_level'] = int(context['level']) + 1
            except ValueError:
                pass

        content = self.nodelist.render(context)
        context['content'] = content
        t = template.loader.get_template('inclusion_tags/container.html')
        resp = t.render(context)
        context.pop()
        return resp


@register.tag('container')
def do_container(parser, token):
    bits = token.split_contents()
    parameters = bits[1:]

    if len(parameters) % 2 != 0:
        raise template.TemplateSyntaxError, '{%% %s param "value" param2 value2 ... %%}' % bits[0]


    parameters = dict((smart_str(key), value) for key, value in zip(parameters[0::2], parameters[1::2]))

    for name in parameters.keys():
        if name not in ('level', 'name', 'css_class', 'title'):
            raise template.TemplateSyntaxError, "%s tag does not accept %r parameter" % (bits[0], name)

    nodelist = parser.parse(('end' + bits[0],))
    parser.delete_first_token()

    return ContainerNode(nodelist, parameters)


