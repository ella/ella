from django import template

from ella.core.models.publishable import Publishable

register = template.Library()


class PublishedByAuthorNode(template.Node):
    def __init__(self, obj_var, count, var_name):
        self.obj_var = obj_var
        self.count = count
        self.var_name = var_name

    def render(self, context):
        try:
            author = template.Variable(self.obj_var).resolve(context)
        except template.VariableDoesNotExist:
            return ''
        published = Publishable.objects.filter(authors__in=[author])[:self.count]
        context[self.var_name] = published
        return ''


@register.tag('published_by_author')
def do_published_by_author(parser, token):
    """
    Get N objects that were published by given author recently.

    **Usage**::

        {% published_by_author <author> <limit> as <result> %}

    **Parameters**::
        ==================================  ================================================
        Option                              Description
        ==================================  ================================================
        ``author``                          Author to load objects for.
        ``limit``                           Maximum number of objects to store,
        ``result``                          Store the resulting list in context under given
                                            name.
        ==================================  ================================================

    **Examples**::

        {% published_by_author object.authors.all.0 10 as article_list %}
    """
    try:
        tag, obj_var, count, fill, var_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError('%r tag requires exactly 4 arguments.' % token.split_contents()[0])
    return PublishedByAuthorNode(obj_var, count, var_name)



