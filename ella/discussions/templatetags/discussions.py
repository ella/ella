import logging

from django import template
from django.template import TemplateSyntaxError
from django.core.paginator import Paginator
from django.conf import settings

from ella.core.models import Listing
from ella.discussions.models import TopicThread, Topic, get_comments_on_thread
from ella.utils.templatetags import parse_getforas_triplet


DISCUSSIONS_PAGINATE_BY = getattr(settings, 'DISCUSSIONS_PAGINATE_BY', 5)

register = template.Library()
log = logging.getLogger('ella.discussions')


# TODO move routine to ella.utils.templatetags?
def parse_getas_tuple(tokens):
    """ parse ``get_something`` **as** ``varname`` """
    tag_name = tokens[0]
    error = TemplateSyntaxError('tag incorrectly written. Format: %s as var_name' % tag_name)
    if len(tokens) != 3:
        raise error
    if tokens[1] != 'as':
        raise error
    return tokens[2]

def topic_from_tpl_var(topic_name, context):
    """ transforms topic_name param (either slug or context variable passed from template) to Topic instance. """
    if topic_name.startswith('"') and topic_name.endswith('"'):
        # topic title passed closed in double quotes
        topics = Topic.objects.filter(slug=topic_name[1:-1])
    else:
        # topic variable passed from template
        topic = context[topic_name]
        if isinstance(topic, Listing):
            topic = topic.placement.target
        if not isinstance(topic, Topic):
            raise TemplateSyntaxError('Variable [%s] is not instance of TopicThread class.' % topic_name)
        topics = Topic.objects.filter(pk=topic._get_pk_val())
    if topics > 0:
        return topics[0]
    return None

def do_tag_process(token, cls):
    """ common processing of discussions get_* template tags """
    tokens = token.split_contents()
    if len(tokens) >= 5:
        tagname, object_definition_tokens, varname = parse_getforas_triplet(tokens)
        return cls(object_definition_tokens, varname)
    elif len(tokens) == 3: # {% template_tag as variable %}
        varname = parse_getas_tuple(tokens)
        return cls(None, varname)
    return cls()

class NewestThreadsNode(template.Node):

    def __init__(self, definition_tokens=None, variable=None):
        self.__tokens = definition_tokens
        self.__variable = variable

    def __get_all(self, context):
        act = [] # TODO man :)
        context[self.__variable] = act
        return ''

    def render(self, context):
        topic_name = self.__tokens[0].strip()
        act = []
        topic = topic_from_tpl_var(topic_name, context)
        if topic:
            act = topic.get_threads_by_date()
            act = map(lambda item: item.__unicode__(), act)
        context[self.__variable] = act
        return ''

class ActiveThreadsNode(template.Node):

    def __init__(self, definition_tokens=None, variable=None):
        self.__tokens = definition_tokens
        self.__variable = variable

    def __get_all(self, context):
        act = []
        for t in Topic.objects.all():
            act.extend(t.get_threads_by_activity())
        context[self.__variable] = act
        return ''

    def render(self, context):
        if not self.__tokens:
            return self.__get_all(context)
        topic_name = self.__tokens[0].strip()
        act = []
        topic = topic_from_tpl_var(topic_name, context)
        if topic:
            act = topic.get_threads_by_activity()
        context[self.__variable] = act
        return ''

class FilledThreadsNode(template.Node):

    def __init__(self, definition_tokens=None, variable=None):
        self.__tokens = definition_tokens
        self.__variable = variable

    def __get_all(self, context):
        out = TopicThread.objects.get_most_filled()
        context[self.__variable] = out
        return ''

    def __get_one(self, topic, context=None):
        if not isinstance(topic, Topic):
            topic = topic_from_tpl_var(topic, context)
        if not topic:
            return []
        return TopicThread.objects.get_most_filled().filter(topic=topic)

    def render(self, context):
        if not self.__tokens:
            return self.__get_all(context)

        topic_name = self.__tokens[0].strip()
        context[self.__variable] = self.__get_one(topic_name, context)
        return ''

class ViewedThreadsNode(template.Node):

    def __init__(self, definition_tokens=None, variable=None):
        self.__tokens = definition_tokens
        self.__variable = variable

    def __get_all(self, context):
        out = TopicThread.objects.get_most_viewed()
        context[self.__variable] = out
        return ''

    def __get_one(self, topic, context=None):
        if not isinstance(topic, Topic):
            topic = topic_from_tpl_var(topic, context)
        if not topic:
            return []
        return TopicThread.objects.get_most_viewed().filter(topic=topic)

    def render(self, context):
        if not self.__tokens:
            return self.__get_all(context)

        topic_name = self.__tokens[0].strip()
        context[self.__variable] = self.__get_one(topic_name, context)
        return ''

class NewestPostsNode(template.Node):

    def __init__(self, definition_tokens=None, variable=None):
        self.__tokens = definition_tokens
        self.__variable = variable

    def __get_all(self, context):
        out = TopicThread.objects.get_most_viewed()
        context[self.__variable] = out
        return ''

    def __get_one(self, topic, context=None):
        if not isinstance(topic, Topic):
            topic = topic_from_tpl_var(topic, context)
        if not topic:
            return []
        return TopicThread.objects.get_with_newest_posts().filter(topic=topic)

    def render(self, context):
        if not self.__tokens:
            return self.__get_all(context)

        topic_name = self.__tokens[0].strip()
        context[self.__variable] = self.__get_one(topic_name, context)
        return ''

class UnreadPostsNode(template.Node):

    def __init__(self, definition_tokens=None, variable=None):
        self.__tokens = definition_tokens
        self.__variable = variable

    def render(self, context):
        out = TopicThread.objects.get_unread_posts()
        context[self.__variable] = out
        return ''

class ItemNumberNode(template.Node):
    def __init__(self, mapping, object, varname, page_varname = None):
        self.mapping, self.object, self.varname, self.page_varname = mapping, object, varname, page_varname

    def render(self, context):
        object = template.Variable(self.object).resolve(context)
        mapping = template.Variable(self.mapping).resolve(context)

        # default value -1 for an object not present in the mapping
        item_number = mapping.get(object._get_pk_val(), -1)
        context[self.varname] = item_number
        if self.page_varname:
            page_number = int(float(item_number)/DISCUSSIONS_PAGINATE_BY + 0.9999)
            context[self.page_varname] = page_number
        return ''

@register.tag
def get_most_active_threads(parser, token):
    """
    Gets most active threads for all topics, or for specific topic.

    Syntax::

        {% get_most_active_threads [for TOPIC as VARNAME] %}

    Example usage::

        {% get_most_active_threads as thr %}
        {% get_most_active_threads for topic_var as active_threads %}
        {% get_most_active_threads for 'svatba' as active_threads %}
    """
    return do_tag_process(token, ActiveThreadsNode)

@register.tag
def get_newest_threads(parser, token):
    """
    Gets newest threads for specific topic.

    Syntax::

        {% get_newest_threads [for TOPIC as VARNAME] %}

    Example usage::

        {% get_newest_threads as thr %}
        {% get_newest_threads for topic_var as thr %}
        {% get_newest_threads for 'svatba' as thr %}
    """
    return do_tag_process(token, NewestThreadsNode)

@register.tag
def get_most_filled_threads(parser, token):
    """
    Get most filled threads for specific topic or all topics.

    Syntax::

        {% get_most_filled_threads [for TOPIC as VARNAME] %}

    Example usage::

        {% get_most_filled_threads as thr %}
        {% get_most_filled_threads for topic_var as thr %}
        {% get_most_filled_threads for 'svatba' as thr %}
    """
    return do_tag_process(token, FilledThreadsNode)

@register.tag
def get_most_viewed_threads(parser, token):
    """
    Get most viewed threads for specific topic or all topics.

    Syntax::

        {% get_most_viewed_threads [for TOPIC as VARNAME] %}

    Example usage::

        {% get_most_viewed_threads as thr %}
        {% get_most_viewed_threads for topic_var as thr %}
        {% get_most_viewed_threads for 'svatba' as thr %}
    """
    return do_tag_process(token, ViewedThreadsNode)

@register.tag
def get_threads_with_newest_posts(parser, token):
    """
    Get threads sorted by date of newest posts within each thread.

    Syntax::

        {% get_threads_with_newest_posts [for TOPIC as VARNAME] %}

    Example usage::

        {% get_threads_with_newest_posts as thr %}
        {% get_threads_with_newest_posts for topic_var as thr %}
        {% get_threads_with_newest_posts for 'svatba' as thr %}
    """
    return do_tag_process(token, NewestPostsNode)

@register.inclusion_tag('inclusion_tags/get_thread_pagination.html', takes_context=True)
def get_thread_pagination(context, thread):
    """
    Renders thread pagination (useful for threads printout) - direct links to specific
    pages within paginated thread.

    Syntax::
        {% get_thread_pagination_per_topic TOPIC %}

    Example usage::
        {% get_thread_pagination_per_topic object %}
    """
    if not isinstance(thread, TopicThread):
        raise TemplateSyntaxError(
            'get_thread_pagination_per_topic - parameter should be valid TopicThread object! Passed arg. type is %s' \
            % str(type(thread))
        )
    qset = get_comments_on_thread(thread)
    p = Paginator(qset, DISCUSSIONS_PAGINATE_BY)
    return {
        'pages': p.pages,
        'has_more_pages': p.pages > 1,
        'page_range': p.page_range,
        'thread_url': thread.get_absolute_url(),
    }

@register.inclusion_tag('inclusion_tags/print_comment_discussions.html', takes_context=True)
def print_comment_discussions(context, comment):
    context['comment'] = comment
    return context

@register.tag
def get_unread_posts(parser, token):
    """
    Get all unread posts for authorized user.

    Syntax::
        {% get_unread_posts %}
    """
    tokens = token.split_contents()
    if len(tokens) == 3: # {% template_tag as variable %}
        varname = parse_getas_tuple(tokens)
    else:
        raise TemplateSyntaxError('Wrong syntax, usage: get_unread_posts as variable.')
    return UnreadPostsNode(None, varname)

@register.tag('get_item_number')
def do_top_rated(parser, token):
    """
    Get item nuber (used for referencing at the page) from a specified object -> number dictionary.

    Usage::

        {% get_item_number from <mapping> for <object> as <varname> page as <page_varname> %}

    Example::

        {% get_item_number from item_number_mapping for obj as item_number %}
    """
    bits = token.split_contents()
    if len(bits) == 7 and bits[1] == 'from' and bits[3] == 'for' and bits[5] == 'as':
        return ItemNumberNode(bits[2], bits[4], bits[6])
    if len(bits) == 10 and bits[1] == 'from' and bits[3] == 'for' and bits[5] == 'as' and bits[7] == 'page' and bits[8] == 'as':
        return ItemNumberNode(bits[2], bits[4], bits[6], bits[9])

