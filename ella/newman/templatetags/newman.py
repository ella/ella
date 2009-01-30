from django import template
from ella.core.cache.utils import get_cached_list

from ella.newman.models import DevMessage

register = template.Library()

class DevMessageNode(template.Node):
    def __init__(self, var_name):
        self.var_name = var_name

    def render(self, ctx):
        qset = get_cached_list(DevMessage)
        ctx[self.var_name] = qset
        return ''

@register.tag
def get_devmsgs(parser, token):
    """Tag that return development messages to newman interface, cached.

    Usage::

        {% get_devmsgs as <var_name> [limit <limit>] [offset <offset>] %}
    """

    bits = token.split_contents()

    return DevMessageNode(bits[2])

