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
[<Comment: comment[1] 'comment on ...' on red apple>]
>>> cmodels.Comment.objects.all()
[<Comment: comment[1] 'comment on ...' on red apple>]

# and to another
>>> package, module = ('sample', 'orange')
>>> contenttype = ContentType.objects.get(app_label__exact=package, model__exact=module)
>>> o_id = Orange.objects.get(cm=10).id
>>> k = cmodels.Comment(target_ct=contenttype, target_id=o_id, content='content on 10kg orange')
>>> k.save()
>>> cmodels.Comment.objects.all()
[<Comment: comment[1] 'comment on ...' on red apple>, <Comment: comment[2] 'content on ...' on 10cm orange>]


# comment forms
>>> from nc.comments import forms as cforms


# simple rendering comment form
>>> c = cforms.CommentForm(opts={'options':'', 'target':'9:1'})
>>> print c.as_p()
<p><label for="id_content">Content:</label> <textarea id="id_content" rows="10" cols="40" name="content"></textarea><input type="hidden" name="parent" id="id_parent" /><input type="hidden" name="hash" value="9631189444103e381fd27ba051f3c4b2" id="id_hash" /><input type="hidden" name="opts" id="id_opts" /><input type="hidden" name="target" value="9:1" id="id_target" /></p>

# valid comment form
>>> c = cforms.CommentForm({'hash':'9631189444103e381fd27ba051f3c4b2', 'opts':'', 'target':'9:1', 'content': 'hohoho'})
>>> c.is_valid()
True
>>> newc = c.save()
>>> cmodels.Comment.objects.all()[2]
<Comment: comment[3] 'hohoho ...' on green apple>

# invalid forms
>>> c = cforms.CommentForm({'hash':'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', 'opts':'', 'target':'9:1', 'content': 'hohoho'})
>>> c.is_valid()
False
>>> c = cforms.CommentForm({'hash':'9631189444103e381fd27ba051f3c4b2', 'opts':'some:invalid:opts', 'target':'9:1', 'content': 'hohoho'})
>>> c.is_valid()
False
>>> c = cforms.CommentForm({'hash':'9631189444103e381fd27ba051f3c4b2', 'opts':'', 'target':'10:5', 'content': 'hohoho'})
>>> c.is_valid()
False



"""


__test__ = {
    'komments_model' : komments_model,
}


if __name__ == '__main__':
    import doctest
    doctest.testmod()

