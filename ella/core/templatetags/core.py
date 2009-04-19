import logging
from hashlib import md5

from django.conf import settings
from django import template
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import smart_str, force_unicode
from django.utils.safestring import mark_safe
from django.template.defaultfilters import stringfilter

from ella.core.models import Listing, Related, Category, LISTING_UNIQUE_DEFAULT_SET
from ella.core.cache.utils import get_cached_object, cache_this
from ella.core.cache.invalidate import CACHE_DELETER
from ella.core.box import BOX_INFO, MEDIA_KEY, Box
from ella.core.middleware import ECACHE_INFO


log = logging.getLogger('ella.core.templatetags')
register = template.Library()

DOUBLE_RENDER = getattr(settings, 'DOUBLE_RENDER', False)

class ListingNode(template.Node):
    def __init__(self, var_name, parameters, parameters_to_resolve):
        self.var_name = var_name
        self.parameters = parameters
        self.parameters_to_resolve = parameters_to_resolve

    def render(self, context):
        unique_var_name = None
        for key in self.parameters_to_resolve:
            if key == 'unique':
                unique_var_name = self.parameters[key]
            if key == 'unique' and unique_var_name not in context.dicts[-1]: # autocreate variable in context
                self.parameters[key] = context.dicts[-1][ unique_var_name ] = set()
                continue
            self.parameters[key] = template.Variable(self.parameters[key]).resolve(context)
        if self.parameters.has_key('category') and isinstance(self.parameters['category'], basestring):
            self.parameters['category'] = get_cached_object(Category, tree_path=self.parameters['category'], site__id=settings.SITE_ID)
        out = Listing.objects.get_listing(**self.parameters)

        if 'unique' in self.parameters:
            unique = self.parameters['unique'] #context[unique_var_name]
            map(lambda x: unique.add(x.placement_id),out)
        context[self.var_name] = out
        return ''

@register.tag
def listing(parser, token):
    """
    Tag that will obtain listing of top (priority-wise) objects for a given category and store them in context under given name.

    Usage::

        {% listing <limit>[ from <offset>][of <app.model>[, <app.model>[, ...]]][ for <category> ] [with children|descendents] as <result> %}

    Parameters:

        ==================================  ================================================
        Option                              Description
        ==================================  ================================================
        ``limit``                           Number of objects to retrieve.
        ``from offset``                     Starting with number (1-based), starts from first
                                            if no offset specified.
        ``of app.model, ...``               List of allowed models, all if omitted.
        ``for category``                    Category of the listing, all categories if not
                                            specified. Can be either string (tree path),
                                            or variable containing a Category object.
        ``with children``                   Include items from direct subcategories.
        ``with descendents``                Include items from all descend subcategories.
        ``as result``                       Store the resulting list in context under given
                                            name.
        ``unique [unique_set_name]``        Unique items across multiple listings.
                                            Name of context variable used to hold the data is optional.
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
        params['unique'] = LISTING_UNIQUE_DEFAULT_SET
        params_to_resolve.append('unique')

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
                lookup_val = template.Variable(self.lookup[1]).resolve(context)
            except template.VariableDoesNotExist:
                lookup_val = self.lookup[1]

            try:
                obj = get_cached_object(self.model, **{self.lookup[0] : lookup_val})
            except models.ObjectDoesNotExist, e:
                log.error('BoxNode: %s (%s : %s)' % (str(e), self.lookup[0], lookup_val))
                return ''
            except AssertionError, e:
                log.error('BoxNode: %s (%s : %s)' % (str(e), self.lookup[0], lookup_val))
                return ''
        else:
            try:
                obj = template.Variable(self.var_name).resolve(context)
            except template.VariableDoesNotExist, e:
                log.error('BoxNode: Template variable does not exist. var_name=%s' % self.var_name)
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
        context[BOX_INFO] = box_key

        # render the box
        result = box.render()
        # restore the context
        context.pop()

        # record parent box dependecy on child box or cached full-page on box
        if not (DOUBLE_RENDER and box.can_double_render) and (BOX_INFO in context or ECACHE_INFO in context):
            if BOX_INFO in context:
                source_key = context[BOX_INFO]
            elif ECACHE_INFO in context:
                source_key = context[ECACHE_INFO]
            CACHE_DELETER.register_dependency(source_key, box_key)

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
            if settings.DEBUG:
                raise template.TemplateSyntaxError, "Model %r does not exist" % bits[3]
            return EmptyNode()

        return BoxNode(bits[1], nodelist, model=model, lookup=(smart_str(bits[5]), bits[6]))

def get_render_key(func, object, content_path):
    if hasattr(object, '_meta'):
        return 'ella.core.templatetags.core.render:%s:%s:%d:%s' % (
                object._meta.app_label,
                object._meta.object_name,
                object.pk,
                content_path
            )
    else:
        return 'ella.core.templatetags.core.render:%s:%s' % (
                md5(smart_str(object)).hexdigest(),
                content_path
            )

def register_test(key, object, content_path):
    CACHE_DELETER.register_pk(object, key)

@cache_this(get_render_key, register_test)
def _render(object, content_path):
    """
    A markdown filter that handles the rendering of any text containing markdown markup and/or django template tags.
    Only ``{{object}}`` and ``{{MEDIA_URL}}`` are available in the context.

    Usage::

        {{object|render:"property.to.render"}}

    Examples::

        {{article|render:"perex"}}
        {{article|render:"content.content"}}
    """
    path = content_path.split('.')
    content = object
    for step in path:
        try:
            content = getattr(content, step)
            if callable(content):
                content = content()
        except:
            # TODO: log
            return ''

    t = template.Template(content)
    return t.render(template.Context({'object' : object, 'MEDIA_URL' : settings.MEDIA_URL}))

@register.filter
def render(object, content_path):
    return mark_safe(_render(object, content_path))

class RenderNode(template.Node):
    def __init__(self, var):
        self.var = template.Variable(var)

    def render(self, context):
        try:
            text = self.var.resolve(context)
        except template.VariableDoesNotExist:
            return ''

        return template.Template(text).render(context)

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

@register.filter
def prefix(string_list, prefix):
    """
    Add prefix to string list (string delimited with spaces). Used for css classes.

    Usage::

        {{string_list|prefix:"pre"}}

    Example::
        {{'a b'|prefix:'x'}}

    Output::

        xa xb
    """
    DELIMITER = ' '
    result = force_unicode(DELIMITER.join([ prefix + i for i in string_list.split(DELIMITER) ]))
    t = template.Template(result)
    return t.render(template.Context({'string_list' : string_list,}))

@register.filter
def suffix(string_list, suffix):
    """
    Add suffix to string list (string delimited with spaces).

    Usage::

        {{string_list|suffix:"pre"}}

    Example::
        {{'a b'|suffix:'x'}}

    Output::

        ax bx
    """
    DELIMITER = ' '
    result = force_unicode(DELIMITER.join([ i + suffix for i in string_list.split(DELIMITER) ]))
    t = template.Template(result)
    return t.render(template.Context({'string_list' : string_list,}))

class RelatedNode(template.Node):
    def __init__(self, obj_var, count, var_name, models=[], all_categories=True):
        """
        Parameters::
        all_categories ... fetches listings even from different categories than obj_var's category
        """
        self.obj_var, self.count, self.var_name, self.models = obj_var, count, var_name, models
        self.all_categories = all_categories

    def render(self, context):
        try:
            obj = template.Variable(self.obj_var).resolve(context)
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
            from ella.tagging.models import TaggedItem
            for m in self.models:
                to_add = TaggedItem.objects.get_related(obj, m, count)
                for rel in to_add:
                    if rel != obj and rel not in related:
                        count -= 1
                        related.append(rel)
                    if count <= 0:
                        break

        # top objects in given category
        if count > 0:
            cat = get_cached_object(Category, pk=obj.category_id)
            listings = Listing.objects.get_listing(category=cat, count=count, mods=self.models)
            ext = [ listing.target for listing in listings if listing.target != obj ]
            related.extend(ext)
            count -= len(ext)
        if self.all_categories and count > 0:
            listings = Listing.objects.get_listing(count=count, mods=self.models)
            related.extend(listing.target for listing in listings if listing.target != obj)

        context[self.var_name] = related
        return ''

@register.tag('related')
def do_related(parser, token):
    """
    Get N related models into a context variable.

    Usage::
        {% related N [app_label.Model, ...] [ALLCATEGORIES] for object as var_name %}

    Example::
        {% related 10 for object as related_list %}
        {% related 10 articles.article, galleries.gallery for object as related_list %}
        {% related 10 articles.article, galleries.gallery ALLCATEGORIES for object as related_list %}
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

    mods_to_slice = -4
    all_categories = False
    if bits[-5] == 'ALLCATEGORIES':
        all_categories = True
        mods_to_slice = -5

    mods = []
    for m in bits[2:mods_to_slice]:
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
    return RelatedNode(bits[-3], int(bits[1]), bits[-1], mods, all_categories)

CONTAINER_VARS = ('level', 'name', 'css_class',)

class ContainerBeginNode(template.Node):
    def __init__(self, parameters):
        self.params = parameters

    def render(self, context):
        context.push()

        for key in CONTAINER_VARS:
            if key not in self.params:
                context[key] = ''
                continue
            value = self.params[key]
            try:
                context[key] = template.Variable(value).resolve(context)
            except template.VariableDoesNotExist:
                context[key] = value

        if 'level' in context:
            try:
                context['next_level'] = int(context['level']) + 1
            except ValueError:
                pass

        t = template.loader.get_template('inclusion_tags/container_begin.html')
        resp = t.render(context)
        return resp

class ContainerEndNode(template.Node):
    def render(self, context):
        t = template.loader.get_template('inclusion_tags/container_end.html')
        resp = t.render(context)
        context.pop()
        return resp

@register.tag
def container_begin(parser, token):
    """
    Render inclusion_tags/container_begin.html template.
    Takes parameters 'level', 'name' and  'css_class' and passes them to the context.
    """
    bits = token.split_contents()
    parameters = bits[1:]

    if len(parameters) % 2 != 0:
        raise template.TemplateSyntaxError, '{%% %s param "value" param2 value2 ... %%}' % bits[0]

    parameters = dict((smart_str(key), value) for key, value in zip(parameters[0::2], parameters[1::2]))

    for name in parameters.keys():
        if name not in CONTAINER_VARS:
            raise template.TemplateSyntaxError, "%s tag does not accept %r parameter" % (bits[0], name)

    return ContainerBeginNode(parameters)

@register.tag
def container_end(parser, token):
    " Render inclusion_tags/container_end.html. "
    return ContainerEndNode()


class CategoriesTreeNode(template.Node):
    def __init__(self, tree_path=None, varname=None, limit=None):
        self.tree_path, self.varname, self.limit = tree_path, varname, limit

    def render(self, ctx):
        if self.tree_path == self.tree_path.strip('"'):
            try:
                root_cat = template.Variable(self.tree_path).resolve(ctx)
            except template.TemplateSyntaxError:
                return ''
        else:
            try:
                root_cat = get_cached_object(Category, tree_path=self.tree_path.strip('"'), site = settings.SITE_ID)
            except Category.DoesNotExist:
                return ''
        try:
            cats = Category.objects.filter(tree_parent=root_cat).order_by('title')
            if self.limit:
                cats = cats[:self.limit]
            ctx.update({self.varname: cats})
        except Category.DoesNotExist:
            pass
        return ''


@register.tag
def get_categories_tree(parser, token):
    """
    Returns sorted categories tree from defined path

    Usage::

        {% get_categories_tree from "<path_tree>" as <varname> limit <limit> %}
        {% get_categories_tree from <category> as <varname> limit <limit> %}
    """

    bits = token.split_contents()
    input_valid = True
    len_bits = len(bits)
    if len_bits not in (5, 7):
        input_valid = False
    if bits[1]!='from' or bits[3]!='as':
        input_valid = False
    if len_bits==7:
        if bits[5]!='limit':
            input_valid = False

    if input_valid:
        if len_bits == 5:
            return CategoriesTreeNode(bits[2], bits[4])
        else:
            return CategoriesTreeNode(bits[2], bits[4], bits[6])
    else:
        raise template.TemplateSyntaxError('Usage of the tag %s: {%% %s from ["<path_tree>"|<category>] as <varname> limit <limit> %%}, where limit is optional (infinite by default).' % (bits[0], bits[0]))
