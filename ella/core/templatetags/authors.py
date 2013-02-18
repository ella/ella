from django import template

register = template.Library()


class AuthorListingNode(template.Node):
    def __init__(self, obj_var, count, var_name, omit_var=None):
        self.obj_var = obj_var
        self.count = int(count)
        self.var_name = var_name
        self.omit_var = omit_var

    def render(self, context):
        try:
            author = template.Variable(self.obj_var).resolve(context)
        except template.VariableDoesNotExist:
            return ''

        if not author:
            return ''

        if self.omit_var is not None:
            try:
                omit = template.Variable(self.omit_var).resolve(context)
            except template.VariableDoesNotExist:
                return ''
        else:
            omit = None

        if omit is not None:
            published = author.recently_published(exclude=omit)
        else:
            published = author.recently_published()

        context[self.var_name] = published[:self.count]
        return ''


@register.tag('author_listing')
def do_author_listing(parser, token):
    """
    Get N listing objects that were published by given author recently and optionally
    omit a publishable object in results.

    **Usage**::

        {% author_listing <author> <limit> as <result> [omit <obj>] %}

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

        {% author_listing object.authors.all.0 10 as article_listing %}
    """
    contents = token.split_contents()

    if len(contents) not in [5, 7]:
        raise template.TemplateSyntaxError('%r tag requires 4 or 6 arguments.' % contents[0])
    elif len(contents) == 5:
        tag, obj_var, count, fill, var_name = contents
        return AuthorListingNode(obj_var, count, var_name)
    else:
        tag, obj_var, count, fill, var_name, filll, omit_var = contents
        return AuthorListingNode(obj_var, count, var_name, omit_var)



