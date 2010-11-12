from django import template
from django.contrib.comments.templatetags import comments as dt
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.utils.encoding import smart_unicode

from threadedcomments.util import annotate_tree_properties, fill_tree
from threadedcomments.templatetags import threadedcomments_tags as tt

from ella.core.models import Publishable
from ella.ellacomments.models import CommentOptionsObject

register = template.Library()

class EllaMixin(object):
    def get_query_set(self, context):
        """
        Override for the django..comments..BaseCommentNode.get_query_set that ignores the site FK
        """
        ctype, object_pk = self.get_target_ctype_pk(context)
        if not object_pk:
            return self.comment_model.objects.none()

        qs = self.comment_model.objects.filter(
            content_type = ctype,
            object_pk    = smart_unicode(object_pk),
        )

        # XXX factor out into a manager
        qs = qs.filter(is_public=True)
        if getattr(settings, 'COMMENTS_HIDE_REMOVED', False):
            qs = qs.filter(is_removed=False)

        return qs

    def get_target_ctype_pk(self, context):
        """
        override of the default behavior that handles Publishables specifically
          - it returns their specific CT
        """
        if self.object_expr:
            try:
                obj = self.object_expr.resolve(context)
            except template.VariableDoesNotExist:
                return None, None

            # if obj is publishable, return correct CT
            if isinstance(obj, Publishable):
                return obj.content_type, obj.pk

            return ContentType.objects.get_for_model(obj), obj.pk
        else:
            return self.ctype, self.object_pk_expr.resolve(context, ignore_failures=True)


# Add the mixins to all Nodes from threadedcomments
class CommentListNode(EllaMixin, tt.CommentListNode): pass
class CommentFormNode(EllaMixin, tt.CommentFormNode): pass
class RenderCommentFormNode(EllaMixin, tt.RenderCommentFormNode): pass
class CommentCountNode(EllaMixin, dt.CommentCountNode): pass

# copied tag registrations from threadedcomments
def get_comment_list(parser, token):
    """
    Gets the list of comments for the given params and populates the template
    context with a variable containing that value, whose name is defined by the
    'as' clause.

    Syntax::

        {% get_comment_list for [object] as [varname] %}
        {% get_comment_list for [app].[model] [object_id] as [varname] %}

    Example usage::

        {% get_comment_list for event as comment_list %}
        {% for comment in comment_list %}
            ...
        {% endfor %}

    """
    return CommentListNode.handle_token(parser, token)

def get_comment_form(parser, token):
    """
    Get a (new) form object to post a new comment.

    Syntax::

        {% get_comment_form for [object] as [varname] %}
        {% get_comment_form for [object] as [varname] with [parent_id] %}
        {% get_comment_form for [app].[model] [object_id] as [varname] %}
        {% get_comment_form for [app].[model] [object_id] as [varname] with [parent_id] %}
    """
    return CommentFormNode.handle_token(parser, token)

def render_comment_form(parser, token):
    """
    Render the comment form (as returned by ``{% render_comment_form %}``) through
    the ``comments/form.html`` template.

    Syntax::

        {% render_comment_form for [object] %}
        {% render_comment_form for [object] with [parent_id] %}
        {% render_comment_form for [app].[model] [object_id] %}
        {% render_comment_form for [app].[model] [object_id] with [parent_id] %}
    """
    return RenderCommentFormNode.handle_token(parser, token)

def annotate_tree(comments):
    return annotate_tree_properties(comments)

# copied from django.comments
def get_comment_count(parser, token):
    """
    Gets the comment count for the given params and populates the template
    context with a variable containing that value, whose name is defined by the
    'as' clause.

    Syntax::

        {% get_comment_count for [object] as [varname]  %}
        {% get_comment_count for [app].[model] [object_id] as [varname]  %}

    Example usage::

        {% get_comment_count for event as comment_count %}
        {% get_comment_count for calendar.event event.id as comment_count %}
        {% get_comment_count for calendar.event 17 as comment_count %}

    """
    return CommentCountNode.handle_token(parser, token)


class CommentOptionsNode(EllaMixin, dt.BaseCommentNode):

    def render(self, context):

        try:
            obj = self.object_expr.resolve(context)
        except template.VariableDoesNotExist:
            return ''

        context.update({
            self.as_varname : CommentOptionsObject.objects.get_for_object(obj)
        })

        return ''

def get_comment_options(parser, token):
    """
    Gets the comment options for the given object.__class__

    Syntax::

        {% get_comment_options for [object] as [varname] %}
        {% get_comment_count for [app].[model] [object_id] as [varname]  %}
    """
    return CommentOptionsNode.handle_token(parser, token)


register.filter(annotate_tree)
register.filter(fill_tree)
register.tag(get_comment_list)
register.tag(get_comment_form)
register.tag(render_comment_form)
register.tag(get_comment_count)
register.tag(get_comment_options)
