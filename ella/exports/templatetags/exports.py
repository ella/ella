from django.conf import settings
from django import template
from django.utils.encoding import smart_str
from django.utils.safestring import mark_safe

register = template.Library()

DOUBLE_RENDER = getattr(settings, 'DOUBLE_RENDER', False)

class PublishableFullUrlNode(template.Node):
    def __init__(self, var_name):
        self.var_name = var_name

    def render(self, context):
        publishable = template.Variable(self.var_name).resolve(context)
        return publishable.get_absolute_url(domain=True)


@register.tag
def publishable_full_url(parser, token):
    tokens = token.split_contents()
    if len(tokens) != 2:
        raise AttributeError('publishable_full_url takes one argument (variable containing publishable object).')
    var_name = tokens[1]
    return PublishableFullUrlNode(var_name)
