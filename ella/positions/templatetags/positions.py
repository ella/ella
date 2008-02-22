from django import template
from django.conf import settings

from ella.utils.templatetags import parse_getforas_triplet
from ella.core.models import Category
from ella.core.cache import get_cached_object
from ella.positions.models import Position


register = template.Library()


@register.tag
def position(parser, token):
    """
    Obtain all active positions for given category or list of categories.
    Put all of them in context variable.
    If some position is not defined for first category, position from next category is used.

    Syntax::

        {% position POSITION_NAME for CATEGORY [nofallback] %}
        {% position POSITION_NAME for CATEGORY using BOX_TYPE [nofallback] %}

    Example usage::

        {% position top_left for category %}
    """
    bits = token.split_contents()
    nodelist = parser.parse(('end' + bits[0],))
    parser.delete_first_token()

    nofallback = False
    if bits[-1] == 'nofallback':
        nofallback = True
        bits.pop()

    if len(bits) == 4 and bits[2] == 'for':
        pos_name, category = bits[1], bits[3]
        box_type = None
    elif len(bits) == 6 and bits[2] == 'for' and bits[4] == 'using':
        pos_name, category, box_type = bits[1], bits[3], bits[5]
    else:
        raise TemplateSyntaxError, 'Invalid syntex: {% position POSITION_NAME for CATEGORY [nofallback] %}'


    return PositionNode(category, pos_name, nodelist, box_type, nofallback)

class PositionNode(template.Node):
    def __init__(self, category, position, nodelist, box_type, nofallback):
        self.category, self.position, self.nodelist, self.box_type = category, position, nodelist, box_type
        self.nofallback = nofallback

    def render(self, context):
        try:
            cat = template.resolve_variable(self.category, context)
            if not isinstance(cat, Category):
                cat = get_cached_object(Category, site=settings.SITE_ID, slug=self.category)
        except template.VariableDoesNotExist, Category.DoesNotExist:
            return ''

        try:
            pos = Position.objects.get_active_position(cat, self.position, self.nofallback)
        except Position.DoesNotExist:
            return ''

        return pos.render(context, self.nodelist, self.box_type)


# TODO: udelat tag: {% position NEWS for CATEGORY using BOX_NAME %}

