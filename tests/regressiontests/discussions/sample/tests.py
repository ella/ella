# --- doc tests for discussions app ---
import logging.config
from settings import *
logging.config.fileConfig(LOGGING_CONFIG_FILE)

banned_strings = r"""
>>> from ella.discussions.models import *
>>> from ella.discussions.views import *
>>> filter_banned_strings(u'A b prdel c d.')
u'A b *** c d.'

>>> filter_banned_strings(u'A b prdel c kurva d.')
u'A b *** c *** d.'

>>> filter_banned_strings(u'A b prdel c kurvaprdel d.')
u'A b *** c ****** d.'

>>> filter_banned_strings(u'A b kujvapudel d.')
u'A b kujvapudel d.'
"""


get_threads_by_date = r"""
>>> from django import template
>>> from django.template import Context, Template
>>> from ella.core.models import Category
>>> from django.contrib.contenttypes.models import ContentType
>>> from ella.discussions.models import *
>>> from ella.discussions.templatetags.discussions import *
>>> categ = Category.objects.get(pk=2)
>>> topic = Topic.objects.get(pk=1)
>>> map(lambda z: z.__unicode__(), topic.get_threads_by_date())
[u'Vlakno Three', u'Vlakno Two', u'Vlakno One']
"""


get_most_active = r"""
>>> from django import template
>>> from django.template import Context, Template
>>> from ella.core.models import Category
>>> from django.contrib.contenttypes.models import ContentType
>>> from ella.discussions.models import *
>>> from ella.discussions.templatetags.discussions import *
>>> for i in Comment.objects.all():
...     i.delete()
>>> categ = Category.objects.get(pk=2)
>>> topic = Topic.objects.get(pk=1)
>>> act = topic.get_threads_by_activity()
>>> map(lambda z: z.__unicode__(), act)
[u'Vlakno Three', u'Vlakno Two', u'Vlakno One']
"""



# template tags test

most_active_tpltag = r"""
>>> tpl = '''
...   {% block container %}
...     {% load discussions %}
...     {% listing 10 of discussions.topic for category as topic_list %}
...     {% for topic in topic_list %}
...         "{{topic.placement.target}}"
...         {% get_most_active_threads for topic as thr_topic %}
...         {% for t in thr_topic %}
...             "{{t}}:{{t.activity}}"
...         {% endfor %}
...     {% endfor %}
...   {% endblock %}
... '''
>>> tpl_lines = tpl.split('\n')
>>> tpl_lines = map(lambda z: z.strip(), tpl_lines)
>>> tpl = ''.join(tpl_lines)

>>> from django import template
>>> from django.template import Context, Template
>>> from ella.core.models import Category
>>> from django.contrib.contenttypes.models import ContentType
>>> from ella.discussions.models import *
>>> from ella.discussions.templatetags.discussions import *
>>> categ = Category.objects.get(pk=2)
>>> t = Template(tpl)
>>> cx = Context({'category': categ})
>>> t.render(cx)
u'"Prvni tema""Vlakno Three:0""Vlakno Two:0""Vlakno One:0""Druhe tema""Vlakno Wife ;-):0""Vlakno Four:0"'
"""


most_active_tpltag_string = r"""
>>> tpl = '''
...   {% block container %}
...     {% load discussions %}
...     {% get_most_active_threads for "prvni-tema" as thr %}
...     {% for i in thr %}
...         "{{i}}:{{i.activity}}"
...     {% endfor %}
...   {% endblock %}
... '''
>>> tpl_lines = tpl.split('\n')
>>> tpl_lines = map(lambda z: z.strip(), tpl_lines)
>>> tpl = ''.join(tpl_lines)
>>> from django import template
>>> from django.template import Context, Template
>>> from ella.core.models import Category
>>> from django.contrib.contenttypes.models import ContentType
>>> from ella.discussions.models import *
>>> from ella.discussions.templatetags.discussions import *
>>> from ella.comments.models import Comment
>>> for i in Comment.objects.all():
...     i.delete()

>>> ct = ContentType.objects.get_for_model(TopicThread)
>>> thr = TopicThread.objects.get(title="Vlakno Two")
>>> c = Comment(content='new comment',subject='',ip_address='1.2.3.4', \
... target_ct=ct,target_id=thr._get_pk_val(),parent=None,user=User.objects.get(username="admin"))
>>> c.save()
>>> c = Comment(content='new comment to vlakno two #2',subject='',ip_address='1.2.3.4', \
... target_ct=ct,target_id=thr._get_pk_val(),parent=None,user=User.objects.get(username="admin"))
>>> c.save()

>>> thr = TopicThread.objects.get(title="Vlakno One")
>>> c = Comment(content='new comment to vlakno one',subject='',ip_address='1.2.3.4', \
... target_ct=ct,target_id=thr._get_pk_val(),parent=None,user=User.objects.get(username="admin"))
>>> c.save()

>>> categ = Category.objects.get(pk=2)
>>> t = Template(tpl)
>>> cx = Context({'category': categ})
>>> t.render(cx)
u'"Vlakno Two:2""Vlakno One:1""Vlakno Three:0"'
"""

most_active_tpltag_without_for = r"""
>>> tpl = '''
...   {% block container %}
...     {% load discussions %}
...     {% get_most_active_threads as thr %}
...     {{thr}}
...   {% endblock %}
... '''
>>> tpl_lines = tpl.split('\n')
>>> tpl_lines = map(lambda z: z.strip(), tpl_lines)
>>> tpl = ''.join(tpl_lines)
>>> from django import template
>>> from django.template import Context, Template
>>> from ella.core.models import Category
>>> from django.contrib.contenttypes.models import ContentType
>>> from ella.discussions.models import *
>>> from ella.discussions.templatetags.discussions import *
>>> for i in Comment.objects.all():
...     i.delete()

>>> ct = ContentType.objects.get_for_model(TopicThread)
>>> thr = TopicThread.objects.get(title="Vlakno Two")
>>> c = Comment(content='new comment',subject='',ip_address='1.2.3.4', \
... target_ct=ct,target_id=thr._get_pk_val(),parent=None,user=User.objects.get(username="admin"))
>>> c.save()
>>> c = Comment(content='new comment to vlakno two #2',subject='',ip_address='1.2.3.4', \
... target_ct=ct,target_id=thr._get_pk_val(),parent=None,user=User.objects.get(username="admin"))
>>> c.save()

>>> thr = TopicThread.objects.get(title="Vlakno One")
>>> c = Comment(content='new comment to vlakno one',subject='',ip_address='1.2.3.4', \
... target_ct=ct,target_id=thr._get_pk_val(),parent=None,user=User.objects.get(username="admin"))
>>> c.save()

>>> categ = Category.objects.get(pk=2)
>>> t = Template(tpl)
>>> cx = Context({'category': categ})
>>> t.render(cx)
u'[&lt;TopicThread: Vlakno Wife ;-)&gt;, &lt;TopicThread: Vlakno Four&gt;, &lt;TopicThread: Vlakno Two&gt;, &lt;TopicThread: Vlakno One&gt;, &lt;TopicThread: Vlakno Three&gt;]'
"""

newest_threads_tpltag = r"""
>>> tpl = '''
...   {% block container %}
...     {% load discussions %}
...     {% listing 10 of discussions.topic for category as topic_list %}
...     {% for topic in topic_list %}
...         "{{topic.placement.target}}"
...         {% get_newest_threads for topic as thr %}
...         {% for i in thr %}
...             "{{i}}"
...         {% endfor %}
...     {% endfor %}
...   {% endblock %}
... '''
>>> tpl_lines = tpl.split('\n')
>>> tpl_lines = map(lambda z: z.strip(), tpl_lines)
>>> tpl = ''.join(tpl_lines)

>>> from django import template
>>> from django.template import Context, Template
>>> from ella.core.models import Category
>>> from django.contrib.contenttypes.models import ContentType
>>> from ella.discussions.models import *
>>> from ella.discussions.templatetags.discussions import *
>>> for i in Comment.objects.all():
...     i.delete()
>>> categ = Category.objects.get(pk=2)
>>> t = Template(tpl)
>>> cx = Context({'category': categ})
>>> t.render(cx)
u'"Prvni tema""Vlakno Three""Vlakno Two""Vlakno One""Druhe tema""Vlakno Wife ;-)""Vlakno Four"'
"""

newest_threads_tpltag_string = r"""
>>> tpl = '''
...   {% block container %}
...     {% load discussions %}
...     {% get_newest_threads for "prvni-tema" as thr %}
...     {% for i in thr %}
...         "{{i}}"
...     {% endfor %}
...   {% endblock %}
... '''
>>> tpl_lines = tpl.split('\n')
>>> tpl_lines = map(lambda z: z.strip(), tpl_lines)
>>> tpl = ''.join(tpl_lines)

>>> from django import template
>>> from django.template import Context, Template
>>> from ella.core.models import Category
>>> from django.contrib.contenttypes.models import ContentType
>>> from ella.discussions.models import *
>>> from ella.discussions.templatetags.discussions import *
>>> for i in Comment.objects.all():
...     i.delete()
>>> categ = Category.objects.get(pk=2)
>>> t = Template(tpl)
>>> cx = Context({'category': categ})
>>> t.render(cx)
u'"Vlakno Three""Vlakno Two""Vlakno One"'
"""

filled_threads_tpltag_string = r"""
>>> tpl = '''
...   {% block container %}
...     {% load discussions %}
...     {% get_most_filled_threads for "druhe-tema" as thr %}
...     {% for i in thr %}
...         "{{i}}"
...     {% endfor %}
...   {% endblock %}
... '''
>>> tpl_lines = tpl.split('\n')
>>> tpl_lines = map(lambda z: z.strip(), tpl_lines)
>>> tpl = ''.join(tpl_lines)

>>> from django import template
>>> from django.template import Context, Template
>>> from ella.core.models import Category
>>> from django.contrib.contenttypes.models import ContentType
>>> from ella.discussions.models import *
>>> from ella.discussions.templatetags.discussions import *
>>> for i in Comment.objects.all():
...     i.delete()
>>> ct = ContentType.objects.get_for_model(TopicThread)
>>> thr_w = TopicThread.objects.get(title="Vlakno Wife ;-)")
>>> thr = TopicThread.objects.get(title="Vlakno Four")
>>> c = Comment(content='new comment',subject='',ip_address='1.2.3.4', \
... target_ct=ct,target_id=thr._get_pk_val(),parent=None,user=User.objects.get(username="admin"))
>>> c.save()
>>> c = Comment(content='new comment to vlakno four #2',subject='',ip_address='1.2.3.4', \
... target_ct=ct,target_id=thr._get_pk_val(),parent=None,user=User.objects.get(username="admin"))
>>> c.save()
>>> c = Comment(content='new comment to vlakno four',subject='',ip_address='1.2.3.4', \
... target_ct=ct,target_id=thr._get_pk_val(),parent=None,user=User.objects.get(username="admin"))
>>> c.save()

>>> thr.num_posts
3
>>> thr_w.num_posts
0

>>> categ = Category.objects.get(pk=2)
>>> t = Template(tpl)
>>> cx = Context({'category': categ})
>>> # UNCOMMENT THIS! t.render(cx)
>>> # TopicThread.objects.get_most_filled().filter(topic=Topic.objects.get(pk=2))
>>> TopicThread.objects.get_most_filled()
[<TopicThread: Vlakno Four>]
"""

filled_threads_tpltag_all = r"""
>>> tpl = '''
...   {% block container %}
...     {% load discussions %}
...     {% get_most_filled_threads as thr %}
...     {% for i in thr %}
...         "{{i}}"
...     {% endfor %}
...   {% endblock %}
... '''
>>> tpl_lines = tpl.split('\n')
>>> tpl_lines = map(lambda z: z.strip(), tpl_lines)
>>> tpl = ''.join(tpl_lines)

>>> from django import template
>>> from django.template import Context, Template
>>> from ella.core.models import Category
>>> from django.contrib.contenttypes.models import ContentType
>>> from ella.discussions.models import *
>>> from ella.discussions.templatetags.discussions import *
>>> for i in Comment.objects.all():
...     i.delete()
>>> Comment.objects.all()
[]

>>> ct = ContentType.objects.get_for_model(TopicThread)
>>> thr_w = TopicThread.objects.get(title="Vlakno Wife ;-)")
>>> thr = TopicThread.objects.get(title="Vlakno Four")
>>> c = Comment(content='new comment',subject='',ip_address='1.2.3.4', \
... target_ct=ct,target_id=thr._get_pk_val(),parent=None,user=User.objects.get(username="admin"))
>>> c.save()
>>> c = Comment(content='new comment to vlakno four #2',subject='',ip_address='1.2.3.4', \
... target_ct=ct,target_id=thr._get_pk_val(),parent=None,user=User.objects.get(username="admin"))
>>> c.save()
>>> c = Comment(content='new comment to vlakno four',subject='',ip_address='1.2.3.4', \
... target_ct=ct,target_id=thr._get_pk_val(),parent=None,user=User.objects.get(username="admin"))
>>> c.save()

>>> thr.num_posts
3
>>> thr_w.num_posts
0

>>> categ = Category.objects.get(pk=2)
>>> t = Template(tpl)
>>> cx = Context({'category': categ})
>>> t.render(cx)
u'"Vlakno Four"'
"""

unread_posts = r"""
>>> from ella.core.models import Category
>>> from django.contrib.contenttypes.models import ContentType
>>> from ella.discussions.models import *
>>> from ella.discussions.templatetags.discussions import *
>>> from ella.discussions.views import add_post
>>> for i in Comment.objects.all():
...     i.delete()
>>> Comment.objects.all()
[]
>>> ct = ContentType.objects.get_for_model(TopicThread)
>>> thr_w = TopicThread.objects.get(title="Vlakno Wife ;-)")
>>> thr = TopicThread.objects.get(title="Vlakno Four")
>>> admin=User.objects.get(username="admin")
>>> add_post('Co vajco', thr, admin)
>>> add_post('Dalsi prispevek', thr, admin)
>>> add_post('Johohohooo!', thr, admin)
>>> normal = User.objects.get(username='normal_user')
>>> for i in TopicThread.objects.get_unread_posts(user=normal):
...    '%s' % i.content
u'Johohohooo!'
u'Dalsi prispevek'
u'Co vajco'

>>> len(TopicThread.objects.get_unread_posts(user=admin))
0

>>> c = Comment.objects.get(content='Johohohooo!', user=admin)
>>> CT = ContentType.objects.get_for_model(Comment)
>>> pv = PostViewed(target_ct=CT, target_id=c._get_pk_val(), user=normal)
>>> pv.save()
>>> for i in TopicThread.objects.get_unread_posts(user=normal):
...    '%s' % i.content
u'Dalsi prispevek'
u'Co vajco'

>>> TopicThread.objects.get_unread_topicthreads(normal)
[<TopicThread: Vlakno Four>]
"""

unread_posts_tpl_tag = r"""
>>> tpl = '''
...   {% block container %}
...     {% load discussions %}
...     {% get_unread_posts as posts %}
...     {% for i in posts %}
...         "{{i.content}}"
...     {% endfor %}
...   {% endblock %}
... '''
>>> tpl_lines = tpl.split('\n')
>>> tpl_lines = map(lambda z: z.strip(), tpl_lines)
>>> tpl = ''.join(tpl_lines)

>>> from django import template
>>> from django.template import Context, Template
>>> from ella.core.models import Category
>>> from django.contrib.contenttypes.models import ContentType
>>> from ella.discussions.models import *
>>> from ella.discussions.templatetags.discussions import *
>>> for i in Comment.objects.all():
...     i.delete()
>>> Comment.objects.all()
[]

>>> ct = ContentType.objects.get_for_model(TopicThread)
>>> thr_w = TopicThread.objects.get(title="Vlakno Wife ;-)")
>>> thr = TopicThread.objects.get(title="Vlakno Four")
>>> c = Comment(content='new comment',subject='',ip_address='1.2.3.4', \
... target_ct=ct,target_id=thr._get_pk_val(),parent=None,user=User.objects.get(username="admin"))
>>> c.save()
>>> c = Comment(content='new comment to vlakno four #2',subject='',ip_address='1.2.3.4', \
... target_ct=ct,target_id=thr._get_pk_val(),parent=None,user=User.objects.get(username="admin"))
>>> c.save()
>>> c = Comment(content='new comment to vlakno four',subject='',ip_address='1.2.3.4', \
... target_ct=ct,target_id=thr._get_pk_val(),parent=None,user=User.objects.get(username="admin"))
>>> c.save()
>>> ctComment = ContentType.objects.get_for_model(Comment)
>>> pv = PostViewed(target_ct=ctComment, target_id=c._get_pk_val(), user=User.objects.get(username="admin"))
>>> pv.save()

>>> categ = Category.objects.get(pk=2)
>>> t = Template(tpl)
>>> cx = Context({'category': categ})
>>> t.render(cx)
u''
"""


most_viewed_threads = """
>>> from ella.discussions.models import TopicThread
>>> TopicThread.objects.get_most_viewed()
[<TopicThread: Vlakno Wife ;-)>, <TopicThread: Vlakno Four>, <TopicThread: Vlakno Three>, <TopicThread: Vlakno Two>, <TopicThread: Vlakno One>]
"""



__test__ = {
    'discussions_filter_banned_strings': banned_strings,
    'discussions_threads_by_date': get_threads_by_date,
    'discussions_most_active': get_most_active,
    'discussions_most_active_template_tag': most_active_tpltag,
    'discussions_most_active_template_tag_string': most_active_tpltag_string,
    'disucssions_most_active_template_tag_without_for': most_active_tpltag_without_for,
    'discussions_newest_threads_template_tag': newest_threads_tpltag,
    'discussions_newest_threads_template_tag_string': newest_threads_tpltag_string,
    'discussions_filled_threads_template_tag_string': filled_threads_tpltag_string,
    'discussions_filled_threads_template_tag_all_topics': filled_threads_tpltag_all,
    'discussions_unread_posts': unread_posts,
    'discussions_most_viewed_threads': most_viewed_threads,

    #'discussions_unread_posts_tpl_tag': unread_posts_tpl_tag,
    #'discussions_filled_threads_template_tag_string': filled_threads_tpltag_string,
    #'discussions_filled_threads_template_tag_all_topics': filled_threads_tpltag_all,
}

