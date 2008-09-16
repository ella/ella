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
        # TODO: caching

        # Get placement
        placement = template.Variable(self.params['for']).resolve(context)

        try:
            if isinstance(placement.target, Serie):
                parts = placement.target.parts
            else:
                current_part = SeriePart.objects.get(placement=placement)
                parts = current_part.serie.parts

                # Shall I hide newer parts?
                if current_part.serie.hide_newer_parts:
                    parts = parts.filter(placement__publish_from__lte=current_part.placement.publish_from)

                # Limit
                if self.params.has_key('limit'):
                    current_index = list(parts).index(current_part)
                    limit = int(self.params['limit'])
                    lo = current_index - limit
                    hi = current_index + limit + 1
                    parts = parts[ lo>0 and lo or 0 : hi ]

        except SeriePart.DoesNotExist:
            return ''

        context[self.params['as']] = parts
        return ''
