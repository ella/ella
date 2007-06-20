komments_model = r"""
>>> print 'ahoj'
ahoj

>>> from nc.comments import models as cmodels
>>> from komments.sample.models import Apple, Orange
>>> from django.contrib.contenttypes.models import ContentType

# few init instances
>>> Orange(cm=10).save()
>>> Orange(cm=20).save()
>>> Apple(color='green').save()
>>> Apple(color='red').save()



# get contenttype for model in app
>>> package, module = ('sample', 'apple')
>>> contenttype = ContentType.objects.get(app_label__exact=package, model__exact=module)
>>> contenttype
<ContentType: apple>
>>> a1 = Apple.objects.get(color='red')
>>> a2 = contenttype.get_object_for_this_type(pk=a1.id)
>>> a1 == a2
True

# try to put a comment on one object
>>> k = cmodels.Comment(target_ct=contenttype, target_id=a1.id, content='comment on red apple')
>>> k.save()
>>> cmodels.Comment.objects.filter(target_ct=contenttype, target_id=a1.id)
[<Comment: comment[1] 'comment on ...' on red apple {path:/}>]
>>> cmodels.Comment.objects.all()
[<Comment: comment[1] 'comment on ...' on red apple {path:/}>]

# and to another
>>> package, module = ('sample', 'orange')
>>> contenttype = ContentType.objects.get(app_label__exact=package, model__exact=module)
>>> o_id = Orange.objects.get(cm=10).id
>>> k = cmodels.Comment(target_ct=contenttype, target_id=o_id, content='content on 10kg orange')
>>> k.save()
>>> cmodels.Comment.objects.all()
[<Comment: comment[1] 'comment on ...' on red apple {path:/}>, <Comment: comment[2] 'content on ...' on 10cm orange {path:/}>]



# comment forms
>>> from nc.comments import forms as cforms

>>> import datetime, time, re

# get contenttype id for apples
>>> apple_ct_id = ContentType.objects.get(name='apple').id
>>> apple_ct_string = '%d:1' % apple_ct_id

# simple rendering comment form
>>> c = cforms.CommentForm(options={'options':'', 'target':apple_ct_string, 'parent':1,})
>>> sorted(c.fields.keys())
['content', 'email', 'hash', 'nickname', 'options', 'parent', 'password', 'reg_anonym_sel', 'target', 'timestamp', 'username']

>>> now = datetime.datetime.now()
>>> now = int(time.mktime(now.timetuple()))
>>> timestamp = c.fields['timestamp'].initial
>>> timestamp - now < 5
True
>>> str(c['timestamp']) == '<input type="hidden" name="timestamp" value="%s" id="id_timestamp" />' % timestamp
True

>>> hash = c.get_hash('', apple_ct_string, timestamp)
>>> str(c['hash']) == '<input type="hidden" name="hash" value="%s" id="id_hash" />' % hash
True

>>> str(c['options'])
'<input type="hidden" name="options" id="id_options" />'
>>> str(c['parent'])
'<input type="hidden" name="parent" value="1" id="id_parent" />'
>>> str(c['target']) == '<input type="hidden" name="target" value="%s" id="id_target" />' % apple_ct_string
True


# data validation - this form uses hash from PREVIOUSLY generated valid form
>>> c = cforms.CommentForm({'hash': c.fields['hash'].initial, # emulate recieving this form value
...                          'timestamp': c.fields['timestamp'].initial, # same emulate as hash
...                          'options':'', 'target':apple_ct_string, 'parent':1, 'content':'hehehehe',
...                          'reg_anonym_sel':'AN',})
>>> c.is_valid()
True
>>> newc = c.save()

>>> cmodels.Comment.objects.all()[2]
<Comment: comment[3] 'hehehehe ...' on green apple {path:/1/}>


# get valid hash
>>> c = cforms.CommentForm()
>>> hash = c.get_hash('', apple_ct_string, 1181143017)

# hash is valid for this options, timestamp, target combination, but form is too old
>>> c = cforms.CommentForm({'hash':hash, 'timestamp':'1181143017',
...                          'options':'', 'target':apple_ct_string, 'parent':1,
...                          'content':'hehehehe',
...                          'reg_anonym_sel':'AN',})
>>> c.is_valid()
False
>>> c.errors.keys()
['timestamp']


# form with little options
>>> c = cforms.CommentForm(options={'options':'lo', 'target':apple_ct_string, 'parent':1,})
>>> sorted(c.fields.keys())
['content', 'hash', 'options', 'parent', 'password', 'target', 'timestamp', 'username']



# create test user
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





"""


__test__ = {
    'komments_model' : komments_model,
}


if __name__ == '__main__':
    import doctest
    doctest.testmod()



