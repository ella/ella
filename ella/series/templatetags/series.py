from django import template

from ella.series.models import Serie, SeriePart

register = template.Library()

@register.tag
def get_serie(parser, token):
    """
    Template tag get_serie.

    Usage::
        {% get_serie for <placement>[ limit <X>] as <result> %}

    Examples::

        {% get_serie for placement as serie %}
        {% get_serie for placement limit 10 as serie %}
    """
    params = get_serie_parse(token.split_contents())
    return SerieNode(params)

def get_serie_parse(input):
    if len(input) < 5:
        raise template.TemplateSyntaxError("Two or more arguments are expected in %r tag" % input[0])
    params = {}

    o = 1
    # for
    if input[o] == 'for':
        params['for'] = input[o+1]
    else:
        raise template.TemplateSyntaxError("Unknown argument %r in tag %r" % (input[o], input[0]))
    o = 3
    # limit
    if input[o] == 'limit':
        params['limit'] = input[o+1]
        o = o + 2
    # as
    if input[o] == 'as':
        params['as'] = input[o+1]
    else:
        raise template.TemplateSyntaxError("%r tag requires 'as' argument" % (input[0]))

    return params

class SerieNode(template.Node):
    def __init__(self, params):
        self.params = params

    def render(self, context):
        placement = template.Variable(self.params['for']).resolve(context)

        if isinstance(placement.publishable.target, Serie):
            # Get all parts for serie without unpublished parts
            parts = placement.publishable.target.parts
        else:
            # Get parts for current part according to parameters

            try:
                current_part = SeriePart.objects.get_part_for_placement(placement)
            except SeriePart.DoesNotExist:
                return ''

            parts = SeriePart.objects.get_serieparts_for_current_part(current_part)

            # Limit
            if self.params.has_key('limit'):
                current_index = parts.index(current_part)
                limit = int(self.params['limit'])
                lo = current_index - limit
                hi = current_index + limit + 1
                parts = parts[ lo>0 and lo or 0 : hi ]

        context[self.params['as']] = parts
        return ''

@register.inclusion_tag('inclusion_tags/serie_navigation.html')
def serie_navigation(placement):
    """
    Standard prev/next navigation in serie, under object

    Usage::

        {% serie_navigation <placement> %}
    """

    out = {}

    try:
        part = SeriePart.objects.get_part_for_placement(placement)
    except SeriePart.DoesNotExist:
        return out

    out['current'] = part
    parts = SeriePart.objects.get_serieparts_for_current_part(part)
    current_index = parts.index(part)

    if (current_index) > 0:
        out['prev'] = parts[current_index-1]
    if (current_index+1) < len(parts):
        out['next'] = parts[current_index+1]

    return out
