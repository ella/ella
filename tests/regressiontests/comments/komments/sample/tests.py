

pokus = r"""
>>> from django.contrib.contenttypes.models import ContentType

>>> from nc.comments import models as cmodels
>>> from nc.comments import forms  as cforms
>>> from nc.comments import defaults as cdefaults

>>> from komments.sample import models as tmodels

>>> import pprint, datetime, time
>>> from django import newforms as forms


# few init instances
>>> tmodels.Orange(cm=10).save()
>>> tmodels.Orange(cm=20).save()
>>> tmodels.Apple(color='green').save()
>>> tmodels.Apple(color='red').save()

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
['content', 'email', 'gonzo', 'nickname', 'options', 'parent', 'password', 'reg_anonym_sel', 'target', 'timestamp', 'username']

# form with target
>>> INIT_PROPS = {
...    'target': apple_red_target,
...}
>>> cform = cforms.CommentForm(init_props=INIT_PROPS)
>>> sorted(cform.fields.keys())
['content', 'email', 'gonzo', 'nickname', 'options', 'parent', 'password', 'reg_anonym_sel', 'target', 'timestamp', 'username']

# form with options
>>> INIT_PROPS = {
...    'target': apple_red_target,
...    'options': 'LO',
...}
>>> cform = cforms.CommentForm(init_props=INIT_PROPS)
>>> sorted(cform.fields.keys())
['content', 'gonzo', 'options', 'parent', 'password', 'target', 'timestamp', 'username']

>>> cf_unbound = cform


# FORM VALIDATION

# too old form
>>> timestamp = datetime.datetime.now() - datetime.timedelta(0, cdefaults.FORM_TIMEOUT + 10)
>>> timestamp = int(timestamp.strftime('%s'))
>>> options = ''
>>> hash = cform.get_hash(options=options, target=apple_red_target, timestamp=timestamp)
>>> DATA = {'gonzo': hash, 'timestamp': timestamp, 'options': options, 'target': apple_red_target,
... 'reg_anonym_sel': 'AN', 'nickname': 'Jantar', 'content': 'Ahoj lidi.',}
>>> cf = cforms.CommentForm(DATA)
>>> sorted(cf.errors.keys()) == ['timestamp']
True

# invalid hash
>>> timestamp = datetime.datetime.now() - datetime.timedelta(0, cdefaults.FORM_TIMEOUT / 2)
>>> timestamp = int(timestamp.strftime('%s'))
>>> options = ''
>>> hash = 'xxxx'
>>> DATA = {'gonzo': hash, 'timestamp': timestamp, 'options': options, 'target': apple_red_target,
... 'reg_anonym_sel': 'AN', 'nickname': 'Jantar', 'content': 'Ahoj lidi.',}
>>> cf = cforms.CommentForm(DATA)
>>> sorted(cf.errors.keys()) == ['gonzo']
True


# invalid target
>>> timestamp = datetime.datetime.now() - datetime.timedelta(0, cdefaults.FORM_TIMEOUT / 2)
>>> timestamp = int(timestamp.strftime('%s'))
>>> options = ''
>>> hash = cform.get_hash(options=options, target=apple_red_target, timestamp=timestamp)
>>> DATA = {'gonzo': hash, 'timestamp': timestamp, 'options': options, 'target': 'x:x',
... 'reg_anonym_sel': 'AN', 'nickname': 'Jantar', 'content': 'Ahoj lidi.',}
>>> cf = cforms.CommentForm(DATA)
>>> sorted(cf.errors.keys()) == ['__all__', 'gonzo', 'target']
True


# invalid options, almost same as invalid hash
>>> timestamp = datetime.datetime.now() - datetime.timedelta(0, cdefaults.FORM_TIMEOUT / 2)
>>> timestamp = int(timestamp.strftime('%s'))
>>> options = ''
>>> hash = cform.get_hash(options=options, target=apple_red_target, timestamp=timestamp)
>>> DATA = {'gonzo': hash, 'timestamp': timestamp, 'options': options, 'target': 'x:x',
... 'reg_anonym_sel': 'AN', 'nickname': 'Jantar', 'content': 'Ahoj lidi.',}
>>> cf = cforms.CommentForm(DATA)
>>> sorted(cf.errors.keys()) == ['__all__', 'gonzo', 'target']
True

# missing username, password if reg_anonym_sel is set to RE
>>> timestamp = datetime.datetime.now() - datetime.timedelta(0, cdefaults.FORM_TIMEOUT / 2)
>>> timestamp = int(timestamp.strftime('%s'))
>>> options = ''
>>> hash = cform.get_hash(options=options, target=apple_red_target, timestamp=timestamp)
>>> DATA = {'gonzo': hash, 'timestamp': timestamp, 'options': options, 'target': apple_red_target,
... 'reg_anonym_sel': 'RE', 'nickname': 'Jantar', 'content': 'Ahoj lidi.',}
>>> cf = cforms.CommentForm(DATA)
>>> sorted(cf.errors.keys()) == ['password', 'username']
True

# missing nickname if reg_anonym_sel is set to AN
>>> timestamp = datetime.datetime.now() - datetime.timedelta(0, cdefaults.FORM_TIMEOUT / 2)
>>> timestamp = int(timestamp.strftime('%s'))
>>> options = ''
>>> hash = cform.get_hash(options=options, target=apple_red_target, timestamp=timestamp)
>>> DATA = {'gonzo': hash, 'timestamp': timestamp, 'options': options, 'target': apple_red_target,
... 'reg_anonym_sel': 'AN', 'username': 'USER', 'password': 'PASSWORD', 'content': 'Ahoj lidi.',}
>>> cf = cforms.CommentForm(DATA)

>>> sorted(cf.errors.keys()) == ['nickname']
True

# save options in db
>>> yearafter = datetime.datetime.now() + datetime.timedelta(365)
>>> cformopt = cmodels.CommentOptions(target_ct=apple_ct, target_id=apple_red.id, options='LO', timestamp=yearafter)
>>> cformopt.save()
>>> cformopt.options == 'LO'
True

# invalid options with db check
>>> timestamp = int(yearafter.strftime('%s')) + 1
>>> options = ''
>>> hash = cform.get_hash(options=options, target=apple_red_target, timestamp=timestamp)
>>> DATA = {'gonzo': hash, 'timestamp': timestamp, 'options': options, 'target': apple_red_target,
... 'reg_anonym_sel': 'RE', 'username': 'USER', 'password': 'PASSWORD', 'content': 'Ahoj lidi.',}
>>> cf = cforms.CommentForm(DATA)
>>> sorted(cf.errors.keys()) == ['__all__', 'gonzo']
True

# invalid timestamp with db check
>>> timestamp = datetime.datetime.now() - datetime.timedelta(0, cdefaults.FORM_TIMEOUT / 2)
>>> timestamp = int(timestamp.strftime('%s'))
>>> options = 'LO'
>>> hash = cform.get_hash(options=options, target=apple_red_target, timestamp=timestamp)
>>> DATA = {'gonzo': hash, 'timestamp': timestamp, 'options': options, 'target': apple_red_target,
... 'reg_anonym_sel': 'RE', 'username': 'USER', 'password': 'PASSWORD', 'content': 'Ahoj lidi.',}
>>> cf = cforms.CommentForm(DATA)
>>> sorted(cf.errors.keys()) == ['__all__', 'timestamp']
True


# user validation and blacklist
>>> from django.contrib.auth.models import User
>>> User.objects.all()
[]
>>> u = User(username='testuser')
>>> u.set_password('testpassword')
>>> u.save()
>>> User.objects.all()
[<User: testuser>]
>>> a = User.objects.get(username='testuser')
>>> a.check_password('testpassword')
True

# logged users only discussion and real user but bad password
>>> timestamp = datetime.datetime.now() - datetime.timedelta(0, cdefaults.FORM_TIMEOUT / 2)
>>> timestamp = int(timestamp.strftime('%s'))
>>> options = 'LO'
>>> target = apple_green_target
>>> hash = cform.get_hash(options=options, target=target, timestamp=timestamp)
>>> DATA = {'gonzo': hash, 'timestamp': timestamp, 'options': options, 'target': target,
... 'username': 'testuser', 'password': 'TESTPASSWORD', 'content': 'Ahoj lidi.',}
>>> cf = cforms.CommentForm(DATA)
>>> cf.is_valid()
False
>>> cf.errors
{'__all__': [u'Invalid user.']}

# bann one user
>>> u = User(username='banneduser')
>>> u.set_password('bannedpassword')
>>> u.save()
>>> b = cmodels.BannedUser(target_ct=apple_ct, target_id=apple_green.id, user=u)
>>> b.save()

# bad user
>>> DATA = {'gonzo': hash, 'timestamp': timestamp, 'options': options, 'target': target,
... 'username': 'banneduser', 'password': 'bannedpassword', 'content': 'Ahoj lidi.',}
>>> cf = cforms.CommentForm(DATA)
>>> cf.is_valid()
False
>>> cf.errors
{'__all__': [u'Banned user.']}

>>> cf_invalid = cf

# and good password
>>> DATA = {'gonzo': hash, 'timestamp': timestamp, 'options': options, 'target': target,
... 'reg_anonym_sel': 'RE', 'username': 'testuser', 'password': 'testpassword', 'content': 'Ahoj lidi.',}
>>> cf = cforms.CommentForm(DATA)
>>> cf.is_valid()
True

>>> cf_valid = cf

# SAVE()

# try to save invalid form
>>> cf_invalid.save()
Traceback (most recent call last):
  File "<stdin>", line 1, in ?
Invalid form: you cannot save invalid form

# try to save unbound form
>>> cf_unbound.save()
Traceback (most recent call last):
  File "<stdin>", line 1, in ?
Invalid form: you cannot save invalid form

# save valid form
>>> sorted(cf_valid.cleaned_data.keys())
['content', 'gonzo', 'options', 'parent', 'password', 'target', 'target_ct', 'target_id', 'timestamp', 'user', 'username']

>>> cmodels.Comment.objects.all()
[]

# emulate fast send clicking
>>> for i in range(1, 10):
...     cf_valid.save()

>>> cmodels.Comment.objects.all()
[<Comment: comment[1] 'Ahoj lidi. ...' on green apple {path:/}>]

>>> cmodels.Comment.objects.get(pk=1).user.username
'testuser'

# redefine new timeout
>>> OLD_TIMEOUT = cforms.defaults.POST_TIMEOUT
>>> cforms.defaults.POST_TIMEOUT = 0.1
>>> time.sleep(0.5)
>>> cf_valid.save()
>>> cmodels.Comment.objects.all()
[<Comment: comment[1] 'Ahoj lidi. ...' on green apple {path:/}>, <Comment: comment[2] 'Ahoj lidi. ...' on green apple {path:/}>]

# and put it back
>>> cforms.defaults.POST_TIMEOUT = OLD_TIMEOUT


# save comment from unauthorized user
>>> DATA = {'gonzo': hash, 'timestamp': timestamp, 'options': options, 'target': target,
... 'reg_anonym_sel': 'AN', 'nickname': 'testuser', 'email': 'a@a.cz', 'content': 'Hello',}
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
... 'reg_anonym_sel': 'AN', 'nickname': 'testuser', 'email': 'a@a.cz', 'content': 'Hello',}
>>> cf = cforms.CommentForm(DATA)
>>> cf.is_valid()
True
>>> cf.save()
>>> cmodels.Comment.objects.all()
[<Comment: comment[1] 'Ahoj lidi. ...' on green apple {path:/}>, <Comment: comment[2] 'Ahoj lidi. ...' on green apple {path:/}>, <Comment: comment[3] 'Hello ...' on green apple {path:/}>]


# TODO: add validation, if really all the values were saved into DB







"""






















__test__ = {
    'pokus' : pokus,
}


if __name__ == '__main__':
    import doctest
    doctest.testmod()



