from django.db.models import get_model
from django.template import Library, Node, TemplateSyntaxError, Variable, resolve_variable
from django.utils.translation import ugettext as _

from ella.tagging.models import Tag, TaggedItem
from ella.core.models import Category
from ella.tagging.utils import LINEAR, LOGARITHMIC, PRIMARY_TAG, SECONDARY_TAG
import ella.tagging.utils as utils

register = Library()

def category_from_tpl_var(category_name, context):
    """ transforms topic_name param (either slug or context variable passed from template) to Topic instance. """
    if isinstance(category_name, Category):
        return category_name # this shouldn't occur
    if category_name.startswith('"') and category_name.endswith('"'):
        # topic title passed closed in double quotes
        cats = Category.objects.filter(slug=category_name[1:-1])
        if len(cats) > 0:
            return cats[0]
    # topic variable passed from template
    cat = context[category_name]
    if not isinstance(cat, Category):
        raise TemplateSyntaxError('Variable [%s] is not instance of Category class.' % category_name)
    return cat

class TagsForModelNode(Node):
    def __init__(self, model, context_var, counts):
        self.model = model
        self.context_var = context_var
        self.counts = counts

    def render(self, context):
        model = get_model(*self.model.split('.'))
        if model is None:
            raise TemplateSyntaxError(_('tags_for_model tag was given an invalid model: %s') % self.model)
        context[self.context_var] = Tag.objects.usage_for_model(model, counts=self.counts)
        return ''

class TagCloudForModelNode(Node):
    def __init__(self, model, context_var, **kwargs):
        self.model = model
        self.context_var = context_var
        self.kwargs = kwargs

    def render(self, context):
        model = get_model(*self.model.split('.'))
        if model is None:
            raise TemplateSyntaxError(_('tag_cloud_for_model tag was given an invalid model: %s') % self.model)
        context[self.context_var] = \
            Tag.objects.cloud_for_model(model, **self.kwargs)
        return ''

class TagsForObjectNode(Node):
    def __init__(self, obj, context_var):
        self.obj = Variable(obj)
        self.context_var = context_var

    def render(self, context):
        context[self.context_var] = \
            Tag.objects.get_for_object(self.obj.resolve(context))
        return ''

class TaggedObjectsNode(Node):
    def __init__(self, tag, model, context_var):
        self.tag = Variable(tag)
        self.context_var = context_var
        self.model = model

    def render(self, context):
        model = get_model(*self.model.split('.'))
        if model is None:
            raise TemplateSyntaxError(_('tagged_objects tag was given an invalid model: %s') % self.model)
        context[self.context_var] = \
            TaggedItem.objects.get_by_model(model, self.tag.resolve(context))
        return ''

class TagCloudForCategoryNode(Node):
    def __init__(self, category, context_var, **kwargs):
        self.category = category
        self.context_var = context_var
        self.priority = kwargs.get('priority', None)

    def render(self, context):
        self.category = category_from_tpl_var(self.category, context)
        if self.priority:
            context[ self.context_var ] = \
            Tag.objects.cloud_for_category(self.category, priority=self.priority)
        else:
            context[ self.context_var ] = \
            Tag.objects.cloud_for_category(self.category)
        return ''

@register.tag
def tags_for_model(parser, token):
    """
    Retrieves a list of ``Tag`` objects associated with a given model
    and stores them in a context variable.

    Usage::

       {% tags_for_model [model] as [varname] %}

    The model is specified in ``[appname].[modelname]`` format.

    Extended usage::

       {% tags_for_model [model] as [varname] with counts %}

    If specified - by providing extra ``with counts`` arguments - adds
    a ``count`` attribute to each tag containing the number of
    instances of the given model which have been tagged with it.

    Examples::

       {% tags_for_model products.Widget as widget_tags %}
       {% tags_for_model products.Widget as widget_tags with counts %}

    """
    bits = token.contents.split()
    len_bits = len(bits)
    if len_bits not in (4, 6):
        raise TemplateSyntaxError(_('%s tag requires either three or five arguments') % bits[0])
    if bits[2] != 'as':
        raise TemplateSyntaxError(_("second argument to %s tag must be 'as'") % bits[0])
    if len_bits == 6:
        if bits[4] != 'with':
            raise TemplateSyntaxError(_("if given, fourth argument to %s tag must be 'with'") % bits[0])
        if bits[5] != 'counts':
            raise TemplateSyntaxError(_("if given, fifth argument to %s tag must be 'counts'") % bits[0])
    if len_bits == 4:
        return TagsForModelNode(bits[1], bits[3], counts=False)
    else:
        return TagsForModelNode(bits[1], bits[3], counts=True)

def __cloud_ext_params(bits):
    """ Returns: {'distribution': ..., 'min_count': ..., 'steps': ....} """
    if bits[4] != 'with':
        raise TemplateSyntaxError(_("if given, fourth argument to %s tag must be 'with'") % bits[0])
    kwargs = {}
    len_bits = len(bits)
    for i in range(5, len_bits):
        try:
            #TODO rewrite to regexp
            name, value = bits[i].split('=')
            if name == 'steps' or name == 'min_count':
                try:
                    kwargs[str(name)] = int(value)
                except ValueError:
                    raise TemplateSyntaxError(_("%(tag)s tag's '%(option)s' option was not a valid integer: '%(value)s'") % {
                        'tag': bits[0],
                        'option': name,
                        'value': value,
})
            elif name == 'distribution':
                valid_vals = ('linear', 'log')
                if value in valid_vals:
                    kwargs[str(name)] = {'linear': LINEAR, 'log': LOGARITHMIC}[value]
                else:
                    raise TemplateSyntaxError(_("%(tag)s tag's '%(option)s' option was not a valid choice. Accepted values: '%(values)s'") % {
                        'tag': bits[0],
                        'option': name,
                        'values': str(valid_vals),
})
            elif name == 'priority':
                valid_vals = ('PRIMARY_TAG', 'SECONDARY_TAG')
                if not value in valid_vals:
                    raise TemplateSyntaxError(
                        _("%(tag)s tag's '%(option)s' option was not a valid choice. Accepted values: '%(values)s'"),
                        {
                            'tag': bits[0],
                            'option': name,
                            'values': str(valid_vals),
}
)
                kwargs[str(name)] = getattr(utils, value)
            else:
                raise TemplateSyntaxError(_("%(tag)s tag was given an invalid option: '%(option)s'") % {
                    'tag': bits[0],
                    'option': name,
})
        except ValueError:
            raise TemplateSyntaxError(_("%(tag)s tag was given a badly formatted option: '%(option)s'") % {
                'tag': bits[0],
                'option': bits[i],
})
    return kwargs

@register.tag
def tag_cloud_for_model(parser, token):
    """
    Retrieves a list of ``Tag`` objects for a given model, with tag
    cloud attributes set, and stores them in a context variable.

    Usage::

       {% tag_cloud_for_model [model] as [varname] %}

    The model is specified in ``[appname].[modelname]`` format.

    Extended usage::

       {% tag_cloud_for_model [model] as [varname] with [options] %}

    Extra options can be provided after an optional ``with`` argument,
    with each option being specified in ``[name]=[value]`` format. Valid
    extra options are:

       ``steps``
          Integer. Defines the range of font sizes.

       ``min_count``
          Integer. Defines the minimum number of times a tag must have
          been used to appear in the cloud.

       ``distribution``
          One of ``linear`` or ``log``. Defines the font-size
          distribution algorithm to use when generating the tag cloud.

    Examples::

       {% tag_cloud_for_model products.Widget as widget_tags %}
       {% tag_cloud_for_model products.Widget as widget_tags with steps=9 min_count=3 distribution=log %}

    """
    bits = token.contents.split()
    len_bits = len(bits)
    if len_bits != 4 and len_bits not in range(6, 9):
        raise TemplateSyntaxError(_('%s tag requires either three or between five and seven arguments') % bits[0])
    if bits[2] != 'as':
        raise TemplateSyntaxError(_("second argument to %s tag must be 'as'") % bits[0])
    kwargs = {}
    if len_bits < 5:
        return TagCloudForModelNode(bits[1], bits[3])
    kwargs = __cloud_ext_params(bits)
    return TagCloudForModelNode(bits[1], bits[3], **kwargs)

@register.tag
def tags_for_object(parser, token):
    """
    Retrieves a list of ``Tag`` objects associated with an object and
    stores them in a context variable.

    Usage::

       {% tags_for_object [object] as [varname] %}

    Example::

        {% tags_for_object foo_object as tag_list %}
    """
    bits = token.contents.split()
    if len(bits) != 4:
        raise TemplateSyntaxError(_('%s tag requires exactly three arguments') % bits[0])
    if bits[2] != 'as':
        raise TemplateSyntaxError(_("second argument to %s tag must be 'as'") % bits[0])
    return TagsForObjectNode(bits[1], bits[3])

@register.tag
def tagged_objects(parser, token):
    """
    Retrieves a list of instances of a given model which are tagged with
    a given ``Tag`` and stores them in a context variable.

    Usage::

       {% tagged_objects [tag] in [model] as [varname] %}

    The model is specified in ``[appname].[modelname]`` format.

    The tag must be an instance of a ``Tag``, not the name of a tag.

    Example::

        {% tagged_objects comedy_tag in tv.Show as comedies %}

    """
    bits = token.contents.split()
    if len(bits) != 6:
        raise TemplateSyntaxError(_('%s tag requires exactly five arguments') % bits[0])
    if bits[2] != 'in':
        raise TemplateSyntaxError(_("second argument to %s tag must be 'in'") % bits[0])
    if bits[4] != 'as':
        raise TemplateSyntaxError(_("fourth argument to %s tag must be 'as'") % bits[0])
    return TaggedObjectsNode(bits[1], bits[3], bits[5])

@register.tag
def tag_cloud_for_category(parser, token):
    """
    Retrieves a list of ``Tag`` objects for a given category,
    creates template variable ``varname``.

    Usage::

       {% tag_cloud_for_category [model] as [varname] %}

    The category is specified by template variable or by slug.

    Extended usage::

       {% tag_cloud_for_category [category] as [varname] with [options] %}

    Extra options can be provided after an optional ``with`` argument,
    with each option being specified in ``[name]=[value]`` format. Valid
    extra options are:

       ``priority``
          Constant described by string. Tag priority.
          Possible values: PRIMARY_TAG, SECONDARY_TAG

       ``steps``
          Integer. Defines the range of font sizes.

       ``min_count``
          Integer. Defines the minimum number of times a tag must have
          been used to appear in the cloud.

       ``distribution``
          One of ``linear`` or ``log``. Defines the font-size
          distribution algorithm to use when generating the tag cloud.

    Examples::

       {% tag_cloud_for_category category_variable as widget_tags %}
       {% tag_cloud_for_category "slug-johohooo" as widget_tags %}
       {% tag_cloud_for_category category_variable as widget_tags with priority=PRIMARY_TAG steps=9 min_count=3 distribution=log %}

    """
    bits = token.contents.split()
    len_bits = len(bits)
    if len_bits != 4 and len_bits not in range(6, 9):
        raise TemplateSyntaxError(_('%s tag requires either three or between five and seven arguments') % bits[0])
    if bits[2] != 'as':
        raise TemplateSyntaxError(_("second argument to %s tag must be 'as'") % bits[0])
    kwargs = {}
    category = bits[1]
    var_name = bits[3]
    if len_bits < 5:
        return TagCloudForCategoryNode(category, var_name)
    kwargs = __cloud_ext_params(bits)
    return TagCloudForCategoryNode(category, var_name, **kwargs)

