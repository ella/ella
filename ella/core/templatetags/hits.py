from django import template

from ella.core.models import HitCount


register = template.Library()

class TopVisitedNode(template.Node):
    def __init__(self, count, name, mods=None):
        self.count, self.name, self.mods = count, name, mods

    def render(self, context):
        context[self.name] = HitCount.objects.get_top_objects(self.count)
        return ''

@register.tag('top_visited')
def do_top_visited(parser, token):
    """
    Get list of COUNT top visited objects of given model and store them in context under given name.

    Usage::

        {% top_visited 5 [app.model ...] as var %}

    Example::

        {% top_visited 10 as top_visited_objects %}
        {% for obj in top_visited_objects %}   ...   {% endfor %}

        {% top_visited 10 articles.article as top_articles %}
        {% for article in top_articles %}   ...   {% endfor %}

        {% top_visited 10 articles.article photos.photo as top_objects %}
        {% for obj in top_objects %}   ...   {% endfor %}
    """
    bits = token.split_contents()
    if len(bits) < 3 or bits[-2] != 'as':
        raise template.TemplateSyntaxError, "{% top_visited 5 [app.model ...] as var %}"

    try:
        count = int(bits[1])
    except ValueError:
        raise template.TemplateSyntaxError, "{% top_visited 5 [app.model ...] as var %}"

    mods = []
    for mod in bits[2:-2]:
        model = models.get_model(*mod.split('.', 1))
        if not model:
            raise template.TemplateSyntaxError, "{% top_visited 5 [app.model ...] as var %}"
        mods.append(model)

    return TopVisitedNode(count, bits[-1], mods)

