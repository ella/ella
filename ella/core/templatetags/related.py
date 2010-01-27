from django import template
from django.db import models

from ella.core.models import Related

register = template.Library()

class RelatedNode(template.Node):
    def __init__(self, obj_var, count, var_name, models):
        self.obj_var, self.count, self.var_name, self.models = obj_var, count, var_name, models

    def render(self, context):
        try:
            obj = template.Variable(self.obj_var).resolve(context)
        except template.VariableDoesNotExist:
            return ''

        count = self.count
        related = Related.objects.get_related_for_object(obj, self.count, self.models)
        context[self.var_name] = related
        return ''

def parse_related_tag(bits):
    if len(bits) < 6:
        raise template.TemplateSyntaxError, "{% related N [app_label.Model, ...] for object as var_name %}"

    if not bits[1].isdigit():
        raise template.TemplateSyntaxError, "Count must be an integer."

    if bits[-2] != 'as':
        raise template.TemplateSyntaxError, "Tag must end with as var_name "
    if bits[-4] != 'for':
        raise template.TemplateSyntaxError, "Tag must end with for object as var_name "

    mods = []
    for m in bits[2:-4]:
        if m == ',':
            continue
        if ',' in m:
            ms = m.split(',')
            for msm in ms:
                if not msm:
                    continue
                try:
                    mods.append(models.get_model(*msm.split('.')))
                except:
                    raise template.TemplateSyntaxError, "%r doesn't represent any model." % msm
        else:
            try:
                mods.append(models.get_model(*m.split('.')))
            except:
                raise template.TemplateSyntaxError, "%r doesn't represent any model." % m

    return bits[-3], int(bits[1]), bits[-1], mods


@register.tag('related')
def do_related(parser, token):
    """
    Get N related models into a context variable.

    Usage::
        {% related N [app_label.Model, ...] for object as var_name %}

    Example::
        {% related 10 for object as related_list %}
        {% related 10 articles.article, galleries.gallery for object as related_list %}
    """
    bits = token.split_contents()
    obj_var, count, var_name, mods = parse_related_tag(bits)
    return RelatedNode(obj_var, count, var_name, mods)



