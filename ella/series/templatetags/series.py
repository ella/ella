from datetime import datetime

from django import template

from ella.series.models import Serie, SeriePart

register = template.Library()

@register.tag
def get_serie(parser, token):
    """ template tag get_serie
        {% get_serie for placement %} """
    params = get_serie_parse(token.split_contents())
    return SerieNode(params)

def get_serie_parse(input):
    if len(input) < 3:
        raise template.TemplateSyntaxError(), "%r tag has no argument" % input[0]
    params = {}

    o = 1
    # for
    if input[o] == 'for':
        params['for'] = input[o+1]
    else:
        raise template.TemplateSyntaxError(), "Unknown argument in tag %r" % input[0]

    return params

class SerieNode(template.Node):
    def __init__(self, params):
        self.params = params

    def render(self, context):
        ctx = {}

        # Get target_ct and target_id
        target_ct = template.Variable(self.params['for']).resolve(context).target_ct
        target_id = template.Variable(self.params['for']).resolve(context).target_id
        # and find out this serie part
        serie_part = SeriePart.objects.filter(target_ct=target_ct, target_id=target_id)

        # Find out other pats
        if serie_part:
            ctx['parts'] = []
            ctx['serie_title'] = serie_part[0].serie.title

            now = datetime.now()
            for part in serie_part[0].serie.parts:
                # Skip newer part
                if part.target.main_placement.publish_from > now:
                    continue
                # Is it current part?
                if part.id == serie_part[0].id:
                    url = None
                else:
                    url = part.target.get_absolute_url()
                ctx['parts'].append({'title': part.target, 'part_no': part.part_no, 'url': url})

        context['serie'] = ctx
        return ''
