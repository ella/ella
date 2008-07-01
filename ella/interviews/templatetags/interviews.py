from django import template

register = template.Library()


class IntervieweesNode(template.Node):
    def __init__(self, interview, var_name):
        self.interview, self.var_name = interview, var_name

    def render(self, context):
        try:
            i = template.Variable(self.interview).resolve(context)
            context[self.var_name] = i.get_interviewees(context['user'])
        except template.VariableDoesNotExist, e:
            pass
        return ''

@register.tag('interviewees')
def do_interviewees(parser, token):
    """
    Get list of interviewees enabled for current user.

    Usage::

        {% interviewees for interview as var %}

    """
    bits = token.split_contents()
    if len(bits) != 5 or bits[1] != 'for' or bits[3] != 'as':
        raise template.TemplateSyntaxError('{% interviewees for interview as var %}')
    return IntervieweesNode(bits[2], bits[4])
