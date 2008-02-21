from django import template
from django.conf import settings

from ella.utils.templatetags import parse_getforas_triplet
from ella.core.models import Category
from ella.positions.models import Position


register = template.Library()


@register.tag
def positions(parser, token):
    """
    Obtain all active positions for given category or list of categories.
    Put all of them in context variable.
    If some position is not defined for first category, position from next category is used.

    Syntax::

        {% positions for CATEGORY[,NEXT_CATEGORY[,NEXT_CATEGORY]] as VARNAME %}

    Example usage::

        {% positions for category as active_positions %}
        {% positions for category,homepage as positions_fallback_homepage %}
    """
    tokens = token.split_contents()
    tag_name, categories, var_name = parse_getforas_triplet(tokens)
    categories = categories[0].split(',')
    return PositionsNode(categories, var_name)

class PositionsNode(template.Node):
    def __init__(self, categories, var_name):
        self.categories = categories
        self.var_name = var_name

    def render(self, context):
        cat_positions = []
        positions = {}

        # resolve category variables or use it as category title
        for cat in self.categories:
            if not isinstance(cat, basestring):
                continue
            try:
                pos = Position.objects.get_active_positions(category=template.resolve_variable(cat, context))
            except template.VariableDoesNotExist:
                pos = Position.objects.get_active_positions(category__title=cat, category__site=settings.SITE_ID)
            cat_positions.append(pos)

        # get positions for first category and fallback on follow-ups
        for pos in cat_positions[::-1]:
            positions.update(dict([ (p.name, p) for p in pos ]))

        context[self.var_name] = positions
        return ''


# TODO: udelat tag: {% position NEWS for CATEGORY using BOX_NAME %}

