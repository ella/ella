from datetime import datetime

from django import template

from ella.series.models import Serie, SeriePart

register = template.Library()

@register.tag
def get_serie(parser, token):
    """
    Template tag get_serie.

    Usage::
        {% get_serie for <placement>[ limit <X>] %}

    Examples::

        {% get_serie for placement %}
        {% get_serie for placement limit 10 %}
    """
    params = get_serie_parse(token.split_contents())
    return SerieNode(params)

def get_serie_parse(input):
    if len(input) < 3:
        raise template.TemplateSyntaxError("%r tag has no argument" % input[0])
    params = {}

    o = 1
    # for
    if input[o] == 'for':
        params['for'] = input[o+1]
    else:
        raise template.TemplateSyntaxError("Unknown argument in tag %r" % input[0])

    return params

class SerieNode(template.Node):
    def __init__(self, params):
        self.params = params

    def render(self, context):
        # TODO: caching

        # Get placement
        placement = template.Variable(self.params['for']).resolve(context)

        try:
            serie_part = SeriePart.objects.get(target_ct=placement.target_ct, target_id=placement.target_id)
        except SeriePart.DoesNotExist:
            return ''

        context['serie'] = serie_part.serie
        return ''
