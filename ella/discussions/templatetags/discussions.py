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


def topic_from_tpl_var(topic_name, context):
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
    if len(topics) > 0:
        return topics[0]
    return None

class NewestThreadsNode(template.Node):

    def __init__(self, definition_tokens=None, variable=None):
        self.__tokens = definition_tokens
        self.__variable = variable

    def __get_all(self):
        act = [] # TODO man :)
        return act

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

    def __get_all(self):
        act = []
        for t in Topic.objects.all():
            act.extend(t.get_threads_by_activity())
        return act

    def render(self, context):
        if not self.__tokens:
            return self.__get_all()
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

    def __get_all(self):
        def mycmp(first, second):
            return cmp(first.num_posts, second.num_posts)

        out = []
        for t in Topic.objects.all():
            out.extend(t.get_threads_by_date())
        out.sort(mycmp)
        return out

    def render(self, context):
        if not self.__tokens:
            return self.__get_all()

        def mycmp(first, second):
            if first and second:
                return cmp(first.num_posts, second.num_posts)
            return 0

        topic_name = self.__tokens[0].strip()
        out = []
        topic = topic_from_tpl_var(topic_name, context)
        if topic:
            out = topic.get_threads_by_date()
            tmp = []
            tmp = map(lambda x: tmp.append(x), out)
            tmp.sort(mycmp)
        context[self.__variable] = out
        return ''


def do_tag_process(token, cls):
    tokens = token.split_contents()
    if len(tokens) >= 5:
        tagname, object_definition_tokens, varname = parse_getforas_triplet(tokens)
        return cls(object_definition_tokens, varname)
    return cls()


@register.tag
def get_most_active_threads(parser, token):
    """
    Gets most active threads for all topics, or for specific topic.

    Syntax::

        {% get_most_active_threads [for TOPIC as VARNAME] %}

    Example usage::

        {% get_most_active_threads %}
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

        {% get_newest_threads %}
        {% get_newest_threads for topic_var as active_threads %}
        {% get_newest_threads for 'svatba' as active_threads %}
    """
    return do_tag_process(token, NewestThreadsNode)

@register.tag
def get_most_filled_threads(parser, token):
    """
    Get most filled threads for specific topic or all topics.

    Syntax::

        {% get_most_filled_threads [for TOPIC as VARNAME] %}

    Example usage::

        {% get_most_filled_threads %}
        {% get_most_filled_threads for topic_var as active_threads %}
        {% get_most_filled_threads for 'svatba' as active_threads %}
    """
    return do_tag_process(token, FilledThreadsNode)
