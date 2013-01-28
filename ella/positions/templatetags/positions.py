from django import template
from django.template import TemplateSyntaxError

from ella.core.models import Category
from ella.positions.models import Position


register = template.Library()


def _get_category_from_pars_var(template_var, context):
    '''
    get category from template variable or from tree_path
    '''
    cat = template_var.resolve(context)
    if isinstance(cat, basestring):
        cat = Category.objects.get_by_tree_path(cat)
    return cat


@register.tag
def position(parser, token):
    """
    Render a given position for category.
    If some position is not defined for first category, position from its parent
    category is used unless nofallback is specified.

    Syntax::

        {% position POSITION_NAME for CATEGORY [nofallback] %}{% endposition %}
        {% position POSITION_NAME for CATEGORY using BOX_TYPE [nofallback] %}{% endposition %}

    Example usage::

        {% position top_left for category %}{% endposition %}
    """
    bits = token.split_contents()
    nodelist = parser.parse(('end' + bits[0],))
    parser.delete_first_token()
    return _parse_position_tag(bits, nodelist)


def _parse_position_tag(bits, nodelist):
    nofallback = False
    if bits[-1] == 'nofallback':
        nofallback = True
        bits.pop()

    if len(bits) == 4 and bits[2] == 'for':
        pos_name, category = bits[1], template.Variable(bits[3])
        box_type = None
    elif len(bits) == 6 and bits[2] == 'for' and bits[4] == 'using':
        pos_name, category, box_type = bits[1], template.Variable(bits[3]), bits[5]
    else:
        raise TemplateSyntaxError('Invalid syntax: {% position POSITION_NAME for CATEGORY [nofallback] %}')

    return PositionNode(category, pos_name, nodelist, box_type, nofallback)


class PositionNode(template.Node):
    def __init__(self, category, position, nodelist, box_type, nofallback):
        self.category, self.position = category, position
        self.nodelist, self.box_type = nodelist, box_type
        self.nofallback = nofallback

    def render(self, context):
        cat = _get_category_from_pars_var(self.category, context)
        pos = Position.objects.get_active_position(cat, self.position, self.nofallback)

        if pos:
            return pos.render(context, self.nodelist, self.box_type)

        return ''


@register.tag
def ifposition(parser, token):
    """
    Syntax::

        {% ifposition POSITION_NAME ... for CATEGORY [nofallback] %}
        {% else %}
        {% endifposition %}

    """
    bits = list(token.split_contents())
    end_tag = 'end' + bits[0]

    nofallback = False
    if bits[-1] == 'nofallback':
        nofallback = True
        bits.pop()

    if len(bits) >= 4 and bits[-2] == 'for':
        category = template.Variable(bits.pop())
        pos_names = bits[1:-1]
    else:
        raise TemplateSyntaxError('Invalid syntax: {% ifposition POSITION_NAME ... for CATEGORY [nofallback] %}')

    nodelist_true = parser.parse(('else', end_tag))
    token = parser.next_token()

    if token.contents == 'else':
        nodelist_false = parser.parse((end_tag,))
        parser.delete_first_token()
    else:
        nodelist_false = template.NodeList()

    return IfPositionNode(category, pos_names, nofallback, nodelist_true, nodelist_false)


class IfPositionNode(template.Node):
    def __init__(self, category, positions, nofallback, nodelist_true, nodelist_false):
        self.category, self.positions = category, positions
        self.nofallback, self.nodelist_true, self.nodelist_false = nofallback, nodelist_true, nodelist_false

    def render(self, context):
        cat = _get_category_from_pars_var(self.category, context)

        for pos in self.positions:
            if Position.objects.get_active_position(cat, pos, self.nofallback):
                return self.nodelist_true.render(context)

        return self.nodelist_false.render(context)
