from django.template import Library, Node, TemplateSyntaxError

from ella.sendmail.forms import SendBuddyForm

register = Library()

class SendToBuddyNode(Node):
    def __init__(self, varname):
        self.varname = varname

    def render(self, context):
        init_props = {
            'target': '%d:%d' % (context['content_type'].id, context['object']._get_pk_val()),
        }
        form = SendBuddyForm(init_props=init_props)
        context[self.varname] = form
        return ''

@register.tag
def send_to_buddy_field(parser, token):
    """
    Assigns form 'send link to a buddy' into given template variable.
    Should be called from object_detail view (variables content_type and object should be present in the context).

    Example::
    {% send_to_buddy_field as VAR %}
    """
    tokens = token.contents.split()
    if len(tokens) != 3:
        raise TemplateSyntaxError('Template tag send_to_buddy field should be used like that: {% send_to_buddy_field as VAR %}')
    varname = tokens[2]
    return SendToBuddyNode(varname)
