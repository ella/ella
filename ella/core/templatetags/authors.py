from django import template

register = template.Library()


class PublishedByAuthorNode(template.Node):
    def __init__(self, obj_var, count, var_name, omit_var=None):
        self.obj_var = obj_var
        self.count = count
        self.var_name = var_name
        self.omit_var = omit_var

    def render(self, context):
        try:
            author = template.Variable(self.obj_var).resolve(context)
        except template.VariableDoesNotExist:
            return ''

        published = author.recently_published()

        if self.omit_var is not None:
            try:
                omit = template.Variable(self.omit_var).resolve(context)
                published.exclude(pk=omit.pk)
            except template.VariableDoesNotExist:
                return ''

        context[self.var_name] = published[:self.count]
        return ''


@register.tag('published_by_author')
def do_published_by_author(parser, token):
    """
    Get N objects that were published by given author recently and optionally
    omit a publishable object in results.

    **Usage**::

        {% published_by_author <author> <limit> as <result> [omit <obj>] %}

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
    contents = token.split_contents()

    if len(contents) not in [5, 7]:
        raise template.TemplateSyntaxError('%r tag requires 4 or 6 arguments.' % contents[0])
    elif len(contents) == 5:
        tag, obj_var, count, fill, var_name = contents
        return PublishedByAuthorNode(obj_var, count, var_name)
    else:
        tag, obj_var, count, fill, var_name, filll, omit_var = contents
        return PublishedByAuthorNode(obj_var, count, var_name, omit_var)



