from ella.oldcomments.models import Comment
from ella.oldcomments.forms import CommentForm

from django import template
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.encoding import smart_str
from django.conf import settings

from ella.utils.templatetags import parse_getfor, parse_getforas_triplet
from ella.core.cache import get_cached_object


DOUBLE_RENDER = getattr(settings, 'DOUBLE_RENDER', False)
register = template.Library()


def parse_object_definition(tagname, od_tokens):
    """parse object definition tokens APP_LABEL.MODEL_NAME with FIELD VALUE"""
    if len(od_tokens) == 1:
        obj = od_tokens[0]
    elif len(od_tokens) == 4:
        model = models.get_model(*od_tokens[0].split('.'))
        if model is None:
            raise template.TemplateSyntaxError, "%r tag: Model %r does not exist" % (tagname, od_tokens[0])

        try:
            obj = get_cached_object(model,  **{smart_str(od_tokens[2]) : od_tokens[3]})
        except models.ObjectDoesNotExist:
            raise template.TemplateSyntaxError, "%r tag: Model %r with field %r equal to %r does not exist." % (
                    tagname, od_tokens[0], od_tokens[2], od_tokens[3]
            )
        except AssertionError:
            raise template.TemplateSyntaxError, "%r tag: Model %r with field %r equal to %r does not refer to a single object." % (
                    tagname, od_tokens[0], od_tokens[2], od_tokens[3]
    )
    else:
        raise template.TemplateSyntaxError, "%r tag: Object must be specified by 'APP_LABEL.MODEL_NAME with FIELD VALUE' or given directly" % tagname

    return obj


@register.tag
def get_comment_form(parser, token):
    """
    Gets a comment form for the given params.

    Syntax::

        {% get_comment_form for APP_LABEL.MODEL_NAME with FIELD VALUE [with OPTIONS_STRING] as VARNAME %}
        {% get_comment_form for OBJECT [with OPTIONS_STRING] as VARNAME %}

    Example usage::

        {% get_comment_form for testapp.apple with id 1 with 'LO' as comment_form %}
        {% get_comment_form for object with 'LO' as comment_form %}
        {% get_comment_form for object as comment_form %}
    """
    tokens = token.split_contents()
    tagname, object_definition_tokens, varname = parse_getforas_triplet(tokens)
    if len(object_definition_tokens) > 1 and object_definition_tokens[-2] == u'with':
        form_options = object_definition_tokens[-1]
        object = parse_object_definition(tagname, object_definition_tokens[:-2])
    else:
        form_options = ''
        object = parse_object_definition(tagname, object_definition_tokens)

    return CommentFormNode(object, form_options, varname)


@register.tag
def get_comment_list(parser, token):
    """
    Gets comments for the given params and populates the template context with
    a special comment_package variable, whose name is defined by the ``as`` clause.

    Syntax::

        {% get_comment_list for APP_LABEL.MODEL_NAME with FIELD VALUE as VARNAME [orderby path|submit_date|...] [limit n]%}
        {% get_comment_list for OBJECT as VARNAME [orderby path|submit_date|...] [limit n]%}

    Example usage::

        {% get_comment_list for testapp.apple with id 1 as comment_list orderby path %}
        {% get_comment_list for object as comment_list %}
        {% get_comment_list for object as comment_list limit 5%}

    To get a list of comments in reverse order -- that is, most recent first --
    pass ``minus`` as a prefix to the last param::

        {% get_comment_list for testapp.apple with id 1 as comment_list orderby -submit_date %}
    """
    tokens = token.split_contents()
    limit = None
    if tokens[-2] == u'limit':
        limit = tokens[-1]
        tokens = tokens[0:-2]
    if tokens[-2] == u'orderby':
        orderby = tokens[-1]
        tagname, object_definition_tokens, varname = parse_getforas_triplet(tokens[:-2])
    else:
        orderby = '-submit_date'
        tagname, object_definition_tokens, varname = parse_getforas_triplet(tokens)
    object = parse_object_definition(tagname, object_definition_tokens)

    return CommentListNode(object, orderby, varname, limit)

@register.tag
def comment_count(parser, token):
    """
    Print comment count for the given params.

    Syntax::

        {% comment_count for APP_LABEL.MODEL_NAME with FIELD VALUE %}
        {% comment_count for OBJECT %}

    Example usage::

        {% comment_count for testapp.apple with id 1 %}
        {% comment_count for object %}
    """
    tokens = token.split_contents()
    tagname, object_definition_tokens = parse_getfor(tokens)
    object = parse_object_definition(tagname, object_definition_tokens)

    return CommentCountNode(object, output=True)

@register.tag
def get_comment_count(parser, token):
    """
    Gets comment count for the given params and populates the template context
    with a variable containing that value, whose name is defined by the 'as' clause.

    Syntax::

        {% get_comment_count for APP_LABEL.MODEL_NAME with FIELD VALUE as VARNAME %}
        {% get_comment_count for OBJECT as VARNAME %}

    Example usage::

        {% get_comment_count for testapp.apple with id 1 as comment_count %}
        {% get_comment_count for object as comment_count %}
    """
    tokens = token.split_contents()
    tagname, object_definition_tokens, varname = parse_getforas_triplet(tokens)
    object = parse_object_definition(tagname, object_definition_tokens)

    return CommentCountNode(object, varname)


def resolve_object(context, obj):
    if isinstance(obj, basestring):
        try:
            obj = template.Variable(obj).resolve(context)
        except template.VariableDoesNotExist:
            raise template.TemplateSyntaxError, "Invalid variable '%r'" % obj
    return obj


class CommentFormNode(template.Node):
    def __init__(self, object, form_options, varname):
        self.object = object
        self.form_options = form_options
        self.varname = varname

    def render(self, context):
        object = resolve_object(context, self.object)
        target_ct = ContentType.objects.get_for_model(object)
        target_id = object.id
        init_props = {
            'target': '%d:%d' % (target_ct.id, target_id),
            'options': self.form_options[1:-1], # TODO: beautify this
        }
        context[self.varname] = CommentForm(init_props=init_props)
        return ''

class CommentListNode(template.Node):
    def __init__(self, object, orderby, varname, limit):
        self.object = object
        self.orderby = orderby
        self.limit = limit
        self.varname = varname

    def render(self, context):
        obj = resolve_object(context, self.object)
        comment_list = Comment.objects.get_list_for_object(obj, order_by=self.orderby, limit=self.limit)
        context[self.varname] = comment_list
        return ''


class CommentCountNode(template.Node):
    def __init__(self, object, varname=None, output=False):
        self.object = object
        self.varname = varname
        self.output = output

    def render(self, context):
        object = resolve_object(context, self.object)
        comment_count = Comment.objects.get_count_for_object(object)
        if self.output:
            if DOUBLE_RENDER and 'SECOND_RENDER' not in context:
                return '{%% load comments %%}{%% comment_count for %(app_label)s.%(module_name)s with pk %(pk)s %%}' % {
                    'app_label' : object._meta.app_label,
                    'module_name' : object._meta.module_name,
                    'pk' : object.pk,
                }
            return str(comment_count)
        context[self.varname] = comment_count
        return ''


@register.inclusion_tag('inclusion_tags/print_comment.html', takes_context=True)
def print_comment(context, comment):
    context['comment'] = comment
    return context


@register.inclusion_tag('inclusion_tags/print_comment_long.html', takes_context=True)
def print_comment_long(context, comment):
    context['comment'] = comment
    return context

@register.inclusion_tag('inclusion_tags/print_single_comment.html', takes_context=True)
def print_single_comment(context, comment):
    context['comment'] = comment
    return context
