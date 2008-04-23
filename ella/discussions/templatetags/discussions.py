from django import template
from django.core.exceptions import ObjectDoesNotExist
from ella.core.models import Listing
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.encoding import smart_str
from ella.discussions.models import *
from django.template import TemplateSyntaxError
from ella.utils.templatetags import parse_getforas_triplet


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
            topic = topic.target
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
    elif len(tokens) == 3:
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
            act = map(lambda item: item.__unicode__(), act)
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

        def mycmp(first, second):
            return cmp(second.num_posts, first.num_posts)

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

        def mycmp(first, second):
            return cmp(second.num_posts, first.num_posts)

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

        def mycmp(first, second):
            return cmp(second.num_posts, first.num_posts)

        topic_name = self.__tokens[0].strip()
        context[self.__variable] = self.__get_one(topic_name, context)
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
