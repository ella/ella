

comment_form_test = r"""
>>> from django.contrib.contenttypes.models import ContentType

>>> from ella.comments import models as cmodels
>>> from ella.comments import forms  as cforms
>>> from ella.comments import defaults as cdefaults

>>> from komments.sample import models as tmodels

>>> import pprint, datetime, time
>>> from django import newforms as forms


# get apple target string
>>> apple_ct = ContentType.objects.get(name='apple')
>>> apple_red   = tmodels.Apple.objects.get(color='red')
>>> apple_green = tmodels.Apple.objects.get(color='green')
>>> apple_red_target   = '%d:%d' % (apple_ct.id, apple_red.id)
>>> apple_green_target = '%d:%d' % (apple_ct.id, apple_green.id)


# FORM GENERATION

# create empty form - but form without specified target is for nothing
>>> cform = cforms.CommentForm()
>>> sorted(cform.fields.keys())
['content', 'email', 'gonzo', 'nickname', 'options', 'parent', 'password', 'reg_anonym_sel', 'subject', 'target', 'timestamp', 'username']

# form with target
>>> INIT_PROPS = {
...    'target': apple_red_target,
...}
>>> cform = cforms.CommentForm(init_props=INIT_PROPS)
>>> sorted(cform.fields.keys())
['content', 'email', 'gonzo', 'nickname', 'options', 'parent', 'password', 'reg_anonym_sel', 'subject', 'target', 'timestamp', 'username']

# form with options
>>> INIT_PROPS = {
...    'target': apple_red_target,
...    'options': 'LO',
...}
>>> cform = cforms.CommentForm(init_props=INIT_PROPS)
>>> sorted(cform.fields.keys())
['content', 'gonzo', 'options', 'parent', 'password', 'subject', 'target', 'timestamp', 'username']

>>> cf_unbound = cform


# FORM VALIDATION

# too old form
>>> timestamp = datetime.datetime.now() - datetime.timedelta(0, cdefaults.FORM_TIMEOUT + 10)
>>> timestamp = int(timestamp.strftime('%s'))
>>> options = ''
>>> hash = cform.get_hash(options=options, target=apple_red_target, timestamp=timestamp)
>>> DATA = {'gonzo': hash, 'timestamp': timestamp, 'options': options, 'target': apple_red_target,
... 'reg_anonym_sel': 'AN', 'nickname': 'Jantar', 'content': 'Ahoj lidi.', 'subject': 'prispevek',}
>>> cf = cforms.CommentForm(DATA)
>>> sorted(cf.errors.keys())
['timestamp']

# invalid hash
>>> timestamp = datetime.datetime.now() - datetime.timedelta(0, cdefaults.FORM_TIMEOUT / 2)
>>> timestamp = int(timestamp.strftime('%s'))
>>> options = ''
>>> hash = 'xxxx'
>>> DATA = {'gonzo': hash, 'timestamp': timestamp, 'options': options, 'target': apple_red_target,
... 'reg_anonym_sel': 'AN', 'nickname': 'Jantar', 'content': 'Ahoj lidi.', 'subject': 'prispevek',}
>>> cf = cforms.CommentForm(DATA)
>>> sorted(cf.errors.keys())
['gonzo']


# invalid target
>>> timestamp = datetime.datetime.now() - datetime.timedelta(0, cdefaults.FORM_TIMEOUT / 2)
>>> timestamp = int(timestamp.strftime('%s'))
>>> options = ''
>>> hash = cform.get_hash(options=options, target=apple_red_target, timestamp=timestamp)
>>> DATA = {'gonzo': hash, 'timestamp': timestamp, 'options': options, 'target': 'x:x',
... 'reg_anonym_sel': 'AN', 'nickname': 'Jantar', 'content': 'Ahoj lidi.', 'subject': 'prispevek',}
>>> cf = cforms.CommentForm(DATA)
>>> sorted(cf.errors.keys())
['__all__', 'gonzo', 'target']


# invalid options, almost same as invalid hash
>>> timestamp = datetime.datetime.now() - datetime.timedelta(0, cdefaults.FORM_TIMEOUT / 2)
>>> timestamp = int(timestamp.strftime('%s'))
>>> options = ''
>>> hash = cform.get_hash(options=options, target=apple_red_target, timestamp=timestamp)
>>> DATA = {'gonzo': hash, 'timestamp': timestamp, 'options': options, 'target': 'x:x',
... 'reg_anonym_sel': 'AN', 'nickname': 'Jantar', 'content': 'Ahoj lidi.', 'subject': 'prispevek',}
>>> cf = cforms.CommentForm(DATA)
>>> sorted(cf.errors.keys())
['__all__', 'gonzo', 'target']

# missing username, password if reg_anonym_sel is set to RE
>>> timestamp = datetime.datetime.now() - datetime.timedelta(0, cdefaults.FORM_TIMEOUT / 2)
>>> timestamp = int(timestamp.strftime('%s'))
>>> options = ''
>>> hash = cform.get_hash(options=options, target=apple_red_target, timestamp=timestamp)
>>> DATA = {'gonzo': hash, 'timestamp': timestamp, 'options': options, 'target': apple_red_target,
... 'reg_anonym_sel': 'RE', 'nickname': 'Jantar', 'content': 'Ahoj lidi.', 'subject': 'prispevek',}
>>> cf = cforms.CommentForm(DATA)
>>> sorted(cf.errors.keys())
['password', 'username']

# missing nickname if reg_anonym_sel is set to AN
>>> timestamp = datetime.datetime.now() - datetime.timedelta(0, cdefaults.FORM_TIMEOUT / 2)
>>> timestamp = int(timestamp.strftime('%s'))
>>> options = ''
>>> hash = cform.get_hash(options=options, target=apple_red_target, timestamp=timestamp)
>>> DATA = {'gonzo': hash, 'timestamp': timestamp, 'options': options, 'target': apple_red_target,
... 'reg_anonym_sel': 'AN', 'username': 'USER', 'password': 'PASSWORD', 'content': 'Ahoj lidi.', 'subject': 'prispevek',}
>>> cf = cforms.CommentForm(DATA)

>>> sorted(cf.errors.keys())
['nickname']

# save options in db
>>> yearafter = datetime.datetime.now() + datetime.timedelta(365)
>>> cformopt = cmodels.CommentOptions(target_ct=apple_ct, target_id=apple_red.id, options='LO', timestamp=yearafter)
>>> cformopt.save()
>>> cformopt.options
'LO'

# invalid options with db check
>>> timestamp = int(yearafter.strftime('%s')) + 1
>>> options = ''
>>> hash = cform.get_hash(options=options, target=apple_red_target, timestamp=timestamp)
>>> DATA = {'gonzo': hash, 'timestamp': timestamp, 'options': options, 'target': apple_red_target,
... 'reg_anonym_sel': 'RE', 'username': 'USER', 'password': 'PASSWORD', 'content': 'Ahoj lidi.', 'subject': 'prispevek',}
>>> cf = cforms.CommentForm(DATA)
>>> sorted(cf.errors.keys())
['__all__', 'gonzo']

# invalid timestamp with db check
>>> timestamp = datetime.datetime.now() - datetime.timedelta(0, cdefaults.FORM_TIMEOUT / 2)
>>> timestamp = int(timestamp.strftime('%s'))
>>> options = 'LO'
>>> hash = cform.get_hash(options=options, target=apple_red_target, timestamp=timestamp)
>>> DATA = {'gonzo': hash, 'timestamp': timestamp, 'options': options, 'target': apple_red_target,
... 'reg_anonym_sel': 'RE', 'username': 'USER', 'password': 'PASSWORD', 'content': 'Ahoj lidi.', 'subject': 'prispevek',}
>>> cf = cforms.CommentForm(DATA)
>>> sorted(cf.errors.keys())
['__all__', 'timestamp']


# user validation and blacklist
>>> from django.contrib.auth.models import User

# logged users only discussion and real user but bad password
>>> timestamp = datetime.datetime.now() - datetime.timedelta(0, cdefaults.FORM_TIMEOUT / 2)
>>> timestamp = int(timestamp.strftime('%s'))
>>> options = 'LO'
>>> target = apple_green_target
>>> hash = cform.get_hash(options=options, target=target, timestamp=timestamp)
>>> DATA = {'gonzo': hash, 'timestamp': timestamp, 'options': options, 'target': target,
... 'username': 'commenttestuser', 'password': 'TESTPASSWORD', 'content': 'Ahoj lidi.', 'subject': 'prispevek',}
>>> cf = cforms.CommentForm(DATA)
>>> cf.is_valid()
False
>>> cf.errors
{'__all__': [u'Invalid user.']}

# bann one user
>>> u = User.objects.get(username='banneduser')
>>> b = cmodels.BannedUser(target_ct=apple_ct, target_id=apple_green.id, user=u)
>>> b.save()

# bad user
>>> DATA = {'gonzo': hash, 'timestamp': timestamp, 'options': options, 'target': target,
... 'username': 'banneduser', 'password': 'bannedpassword', 'content': 'Ahoj lidi.', 'subject': 'prispevek',}
>>> cf = cforms.CommentForm(DATA)
>>> cf.is_valid()
False
>>> cf.errors
{'__all__': [u'Banned user.']}

>>> cf_invalid = cf

# and good password
>>> DATA = {'gonzo': hash, 'timestamp': timestamp, 'options': options, 'target': target,
... 'reg_anonym_sel': 'RE', 'username': 'commenttestuser', 'password': 'testpassword', 'content': 'Ahoj lidi.', 'subject': 'prispevek',}
>>> cf = cforms.CommentForm(DATA)
>>> cf.is_valid()
True

>>> cf_valid = cf

# SAVE()

# try to save invalid form
>>> cf_invalid.save()
False

# try to save unbound form
>>> cf_unbound.save()
False

# save valid form
>>> sorted(cf_valid.cleaned_data.keys())
['content', 'gonzo', 'options', 'parent', 'password', 'subject', 'target', 'target_ct', 'target_id', 'timestamp', 'user', 'username']

>>> cmodels.Comment.objects.all()
[]

# emulate fast send clicking
>>> for i in range(1, 10):
...     cf_valid.save()

>>> cmodels.Comment.objects.all()
[<Comment: comment [id:1] 'Ahoj lidi....' on green apple {path:}>]

>>> cmodels.Comment.objects.get(pk=1).user.username
u'commenttestuser'

# redefine new timeout
>>> OLD_TIMEOUT = cforms.defaults.POST_TIMEOUT
>>> cforms.defaults.POST_TIMEOUT = 0.1
>>> time.sleep(0.5)
>>> cf_valid.save()
>>> cmodels.Comment.objects.all()
[<Comment: comment [id:1] 'Ahoj lidi....' on green apple {path:}>, <Comment: comment [id:2] 'Ahoj lidi....' on green apple {path:}>]

# and put it back
>>> cforms.defaults.POST_TIMEOUT = OLD_TIMEOUT


# save comment from unauthorized user
>>> DATA = {'gonzo': hash, 'timestamp': timestamp, 'options': options, 'target': target,
... 'reg_anonym_sel': 'AN', 'nickname': 'commenttestuser', 'email': 'a@a.cz', 'content': 'Hello', 'subject': 'prispevek',}
>>> cf = cforms.CommentForm(DATA)
>>> cf.is_valid()
False
>>> sorted(cf.errors.keys())
['password', 'username']

>>> timestamp = datetime.datetime.now() - datetime.timedelta(0, cdefaults.FORM_TIMEOUT / 2)
>>> timestamp = int(timestamp.strftime('%s'))
>>> options = ''
>>> target = apple_green_target
>>> hash = cform.get_hash(options=options, target=target, timestamp=timestamp)
>>> DATA = {'gonzo': hash, 'timestamp': timestamp, 'options': options, 'target': target,
... 'reg_anonym_sel': 'AN', 'nickname': 'commenttestuser', 'email': 'a@a.cz', 'content': 'Hello', 'subject': 'prispevek',}
>>> cf = cforms.CommentForm(DATA)
>>> cf.is_valid()
True
>>> cf.save()
>>> cmodels.Comment.objects.all()
[<Comment: comment [id:1] 'Ahoj lidi....' on green apple {path:}>, <Comment: comment [id:2] 'Ahoj lidi....' on green apple {path:}>, <Comment: comment [id:3] 'Hello...' on green apple {path:}>]


# TODO: add validation, if really all the values were saved into DB



"""

comment_form_parent = r"""
"""


comment_templatetags = r"""
>>> from ella.comments import models as cmodels
>>> from ella.comments import forms  as cforms
>>> from komments.sample.models import Apple, Orange

>>> from django.contrib.contenttypes.models import ContentType
>>> from django.template import Template, Context

>>> import pprint, datetime, time
>>> from django import newforms as forms


# test get_comment_form
>>> apple = Apple.objects.get(color='red')
>>> t = Template('''
... {% load comments %}
... {% get_comment_form for apple with 'LO' as comment_form %}
... {{comment_form|pprint}}
... ''')
>>> t.render(Context({'apple': apple}))
u"\n\n\nCommentForm for [12:2] with fields ['content', 'gonzo', 'options', 'parent', 'password', 'subject', 'target', 'timestamp', 'username']\n"

>>> apple = Apple.objects.get(color='green')
>>> t = Template('''
... {%% load comments %%}
... {%% get_comment_form for sample.apple with id %d as comment_form %%}
... {{comment_form|pprint}}
... ''' % apple.id)
>>> t.render(Context({'apple': apple}))
u"\n\n\nCommentForm for [12:1] with fields ['content', 'email', 'gonzo', 'nickname', 'options', 'parent', 'password', 'reg_anonym_sel', 'subject', 'target', 'timestamp', 'username']\n"

>>> t = Template('''
... {% load comments %}
... {% get_comment_form for apple as comment_form %}
... {{comment_form|pprint}}
... ''')
>>> t.render(Context({'apple': apple}))
u"\n\n\nCommentForm for [12:1] with fields ['content', 'email', 'gonzo', 'nickname', 'options', 'parent', 'password', 'reg_anonym_sel', 'subject', 'target', 'timestamp', 'username']\n"

>>> t = Template('''
... {%% load comments %%}
... {%% get_comment_form for sample.apple with id %d with 'LO' as comment_form %%}
... {{comment_form|pprint}}
... ''' % apple.id)
>>> t.render(Context({'apple': apple}))
u"\n\n\nCommentForm for [12:1] with fields ['content', 'gonzo', 'options', 'parent', 'password', 'subject', 'target', 'timestamp', 'username']\n"


# test get_comment_list
>>> t = Template('''
... {% load comments %}
... {% get_comment_list for apple as comment_list %}
... {{comment_list|pprint}}
... ''')
>>> t.render(Context({'apple': apple}))
u"\n\n\n[<Comment: comment [id:3] 'Hello...' on green apple {path:}>, <Comment: comment [id:2] 'Ahoj lidi....' on green apple {path:}>, <Comment: comment [id:1] 'Ahoj lidi....' on green apple {path:}>]\n"

>>> t = Template('''
... {%% load comments %%}
... {%% get_comment_list for sample.apple with id %d as comment_list orderby content %%}
... {{comment_list|pprint}}
... ''' % apple.id)
>>> t.render(Context({'apple': apple}))
u"\n\n\n[<Comment: comment [id:1] 'Ahoj lidi....' on green apple {path:}>, <Comment: comment [id:2] 'Ahoj lidi....' on green apple {path:}>, <Comment: comment [id:3] 'Hello...' on green apple {path:}>]\n"


# test get_comment_count
>>> t = Template('''
... {% load comments %}
... {% get_comment_count for apple as comment_count %}
... {{comment_count}}
... ''')
>>> t.render(Context({'apple': apple}))
u'\n\n\n3\n'

>>> t = Template('''
... {%% load comments %%}
... {%% get_comment_count for sample.apple with id %d as comment_count %%}
... {{comment_count}}
... ''' % apple.id)
>>> t.render(Context({'apple': apple}))
u'\n\n\n3\n'

"""

comment_form_options = r"""
>>> from ella.comments import models as cmodels
>>> from ella.comments import forms  as cforms
>>> from komments.sample.models import Apple, Orange

>>> from django.contrib.contenttypes.models import ContentType
>>> from django.template import Template, Context

>>> import pprint, datetime, time
>>> from django import newforms as forms

>>> from komments.sample import models as tmodels

# get apple target string
>>> apple_ct = ContentType.objects.get(name='apple')
>>> apple_red   = tmodels.Apple.objects.get(color='red')
>>> apple_green = tmodels.Apple.objects.get(color='green')
>>> apple_red_target   = '%d:%d' % (apple_ct.id, apple_red.id)
>>> apple_green_target = '%d:%d' % (apple_ct.id, apple_green.id)


# form with options
>>> INIT_PROPS = {
...    'target': apple_red_target,
...    'options': 'UN',
...}
>>> cform = cforms.CommentForm(init_props=INIT_PROPS)
>>> sorted(cform.fields.keys())
['content', 'email', 'gonzo', 'nickname', 'options', 'parent', 'subject', 'target', 'timestamp']

"""











__test__ = {
    'comment_form_test': comment_form_test,
    'comment_templatetags': comment_templatetags,
    'comment_form_options': comment_form_options,
}


if __name__ == '__main__':
    import doctest
    doctest.testmod()



