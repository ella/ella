from nc.comments.models import Comment
from nc.comments.forms import CommentForm

from django import template
from django.template import loader
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType

from django.db.models import get_model

register = template.Library()


class CommentFormNode(template.Node):
    def __init__(self, package, module, context_var_name, obj_id, form_settings, var_name):
        self.package, self.module = package, module
        self.context_var_name, self.obj_id = context_var_name, obj_id
        self.var_name = var_name
        self.form_settings = form_settings

    def render(self, context):
        from django.conf import settings
        try:
            self.obj_id = template.resolve_variable(self.context_var_name, context)
            package, module = self.package, self.module
            content_type = ContentType.objects.get_for_model(get_model(package, module))
            target_ct = content_type.id
        except template.VariableDoesNotExist:
            return ''

        context[self.var_name] = CommentForm(init_props={'target': '%d:%d' % (target_ct, self.obj_id), 'options': self.form_settings})
        return ''

class CommentCountNode(template.Node):
    def __init__(self, package, module, context_var_name, obj_id, var_name):
        self.package, self.module = package, module
        self.context_var_name, self.obj_id = context_var_name, obj_id
        self.var_name = var_name

    def render(self, context):
        from django.conf import settings
        manager = Comment.objects
        if self.context_var_name is not None:
            try:
                self.obj_id = template.resolve_variable(self.context_var_name, context)
            except template.VariableDoesNotExist:
                return ''
        kwargs = {
            'target_id__exact': self.obj_id,
            'target_ct__app_label__exact': self.package,
            'target_ct__model__exact': self.module,
#            'site__id__exact': settings.SITE_ID,
}
        comment_count = manager.filter(**kwargs).count()
        context[self.var_name] = comment_count
        return ''

class CommentListNode(template.Node):
    def __init__(self, package, module, context_var_name, obj_id, var_name, ordering, extra_kwargs=None):
        self.package, self.module = package, module
        self.context_var_name, self.obj_id = context_var_name, obj_id
        self.var_name = var_name
        self.ordering = ordering
        self.extra_kwargs = extra_kwargs or {}

    def render(self, context):
        from django.conf import settings
        get_list_function = Comment.objects.filter
        if self.context_var_name is not None:
            try:
                self.obj_id = template.resolve_variable(self.context_var_name, context)
            except template.VariableDoesNotExist:
                return ''
        kwargs = {
            'target_id__exact': self.obj_id,
            'target_ct__app_label__exact': self.package,
            'target_ct__model__exact': self.module,
#            'site__id__exact': settings.SITE_ID,
}
        kwargs.update(self.extra_kwargs)
        comment_list = get_list_function(**kwargs).order_by(self.ordering + 'submit_date').select_related()
        context[self.var_name] = comment_list
        return ''


class GetCommentForm:
    """
    Displays a comment form for the given params.

    Syntax::

        {% get_comment_form for [pkg].[py_module_name] [context_var_containing_obj_id] with [options string] as [varname] %}

    Example usage::

        {% get_comment_form for lcom.eventtimes event.id with 'LO' as comment_form %}

    ``[context_var_containing_obj_id]`` can be a hard-coded integer or a variable containing the ID.
    """
    def __call__(self, parser, token):
        tokens = token.contents.split()
        # Now tokens is a list like this:
        # ['get_comment_form', 'for', 'lcom.eventtimes', 'event.id', 'with', 'comment_options', 'as', 'comment_form']
        if not (len(tokens) == 6 or len(tokens) == 8):
            raise template.TemplateSyntaxError, "%r tag requires 5 or 7 arguments" % tokens[0]
        if tokens[1] != 'for':
            raise template.TemplateSyntaxError, "Second argument in %r tag must be 'for'" % tokens[0]
        try:
            package, module = tokens[2].split('.')
        except ValueError: # unpack list of wrong size
            raise template.TemplateSyntaxError, "Third argument in %r tag must be in the format 'package.module'" % tokens[0]
        try:
            content_type = ContentType.objects.get_for_model(get_model(package, module))
        except ContentType.DoesNotExist:
            raise template.TemplateSyntaxError, "%r tag has invalid content-type '%s.%s'" % (tokens[0], package, module)
        var_name, obj_id = None, None
        if tokens[3].isdigit():
            obj_id = tokens[3]
            try: # ensure the object ID is valid
                content_type.get_object_for_this_type(pk=obj_id)
            except ObjectDoesNotExist:
                raise template.TemplateSyntaxError, "%r tag refers to %s object with ID %s, which doesn't exist" % (tokens[0], content_type.name, obj_id)
        else:
            var_name = tokens[3]

        if tokens[4] == 'with':
            if len(tokens) != 8 and tokens[6] != 'as':
                raise template.TemplateSyntaxError, "If fourth argument in %r is 'with' it must have also argument 'as'" % tokens[0]
            else:
                # remove quotes 'koko' => koko
                form_settings = tokens[5][1:-1]
                context_var = tokens[7]

        elif tokens[4] == 'as':
            form_settings = ''
            context_var = tokens[5]
        else:
            raise template.TemplateSyntaxError, "Fourth argument in %r must be 'with' or 'as'" % tokens[0]


        return CommentFormNode(package, module, var_name, obj_id, form_settings, context_var)



class GetCommentCount:
    """
    Gets comment count for the given params and populates the template context
    with a variable containing that value, whose name is defined by the 'as'
    clause.

    Syntax::

        {% get_comment_count for [pkg].[py_module_name] [context_var_containing_obj_id] as [varname]  %}

    Example usage::

        {% get_comment_count for lcom.eventtimes event.id as comment_count %}

    Note: ``[context_var_containing_obj_id]`` can also be a hard-coded integer, like this::

        {% get_comment_count for lcom.eventtimes 23 as comment_count %}
    """
    def __call__(self, parser, token):
        tokens = token.contents.split()
        # Now tokens is a list like this:
        # ['get_comment_list', 'for', 'lcom.eventtimes', 'event.id', 'as', 'comment_list']
        if len(tokens) != 6:
            raise template.TemplateSyntaxError, "%r tag requires 5 arguments" % tokens[0]
        if tokens[1] != 'for':
            raise template.TemplateSyntaxError, "Second argument in %r tag must be 'for'" % tokens[0]
        try:
            package, module = tokens[2].split('.')
        except ValueError: # unpack list of wrong size
            raise template.TemplateSyntaxError, "Third argument in %r tag must be in the format 'package.module'" % tokens[0]
        try:
            content_type = ContentType.objects.get_for_model(get_model(package, module))
        except ContentType.DoesNotExist:
            raise template.TemplateSyntaxError, "%r tag has invalid content-type '%s.%s'" % (tokens[0], package, module)
        var_name, obj_id = None, None
        if tokens[3].isdigit():
            obj_id = tokens[3]
            try: # ensure the object ID is valid
                content_type.get_object_for_this_type(pk=obj_id)
            except ObjectDoesNotExist:
                raise template.TemplateSyntaxError, "%r tag refers to %s object with ID %s, which doesn't exist" % (tokens[0], content_type.name, obj_id)
        else:
            var_name = tokens[3]
        if tokens[4] != 'as':
            raise template.TemplateSyntaxError, "Fourth argument in %r must be 'as'" % tokens[0]

        return CommentCountNode(package, module, var_name, obj_id, tokens[5])

class GetCommentList:
    """
    Gets comments for the given params and populates the template context with a
    special comment_package variable, whose name is defined by the ``as``
    clause.

    Syntax::

        {% get_comment_list for [pkg].[py_module_name] [context_var_containing_obj_id] as [varname] (reversed) %}

    Example usage::

        {% get_comment_list for lcom.eventtimes event.id as comment_list %}

    Note: ``[context_var_containing_obj_id]`` can also be a hard-coded integer, like this::

        {% get_comment_list for lcom.eventtimes 23 as comment_list %}

    To get a list of comments in reverse order -- that is, most recent first --
    pass ``reversed`` as the last param::

        {% get_comment_list for lcom.eventtimes event.id as comment_list reversed %}
    """
    def __call__(self, parser, token):
        tokens = token.contents.split()
        # Now tokens is a list like this:
        # ['get_comment_list', 'for', 'lcom.eventtimes', 'event.id', 'as', 'comment_list']
        if not len(tokens) in (6, 7):
            raise template.TemplateSyntaxError, "%r tag requires 5 or 6 arguments" % tokens[0]
        if tokens[1] != 'for':
            raise template.TemplateSyntaxError, "Second argument in %r tag must be 'for'" % tokens[0]
        try:
            package, module = tokens[2].split('.')
        except ValueError: # unpack list of wrong size
            raise template.TemplateSyntaxError, "Third argument in %r tag must be in the format 'package.module'" % tokens[0]
        try:
            content_type = ContentType.objects.get_for_model(get_model(package, module))
        except ContentType.DoesNotExist:
            raise template.TemplateSyntaxError, "%r tag has invalid content-type '%s.%s'" % (tokens[0], package, module)
        var_name, obj_id = None, None
        if tokens[3].isdigit():
            obj_id = tokens[3]
            try: # ensure the object ID is valid
                content_type.get_object_for_this_type(pk=obj_id)
            except ObjectDoesNotExist:
                raise template.TemplateSyntaxError, "%r tag refers to %s object with ID %s, which doesn't exist" % (tokens[0], content_type.name, obj_id)
        else:
            var_name = tokens[3]
        if tokens[4] != 'as':
            raise template.TemplateSyntaxError, "Fourth argument in %r must be 'as'" % tokens[0]
        if len(tokens) == 7:
            if tokens[6] != 'reversed':
                raise template.TemplateSyntaxError, "Final argument in %r must be 'reversed' if given" % tokens[0]
            ordering = "-"
        else:
            ordering = ""

        return CommentListNode(package, module, var_name, obj_id, tokens[5], ordering)

# registration comments
register.tag('get_comment_form', GetCommentForm())
register.tag('get_comment_list', GetCommentList())
register.tag('get_comment_count', GetCommentCount())



