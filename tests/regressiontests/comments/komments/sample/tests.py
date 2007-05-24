komments_model = r"""
>>> print 'ahoj'
ahoj

>>> from nc.comments import models as cmodels
>>> from komments.sample.models import Apple, Orange
>>> from django.contrib.contenttypes.models import ContentType


# few init instances
>>> Orange(weight=10).save()
>>> Orange(weight=20).save()
>>> Apple(color='green').save()
>>> Apple(color='red').save()

# dump my init test data for future move to fixtures/initial_data.json
>>> from django.conf import settings
>>> from django.core import management

#>>> management.syncdb(0, False)
>>> f = file('/tmp/hovno.json', 'w')
>>> f.write(management.dump_data(['sample'], 'json', True))
>>> f.close()


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
[<Comment: comment[1] 'comment on ...' on Apple object>]
>>> cmodels.Comment.objects.all()
[<Comment: comment[1] 'comment on ...' on Apple object>]

# and to another
>>> package, module = ('sample', 'orange')
>>> contenttype = ContentType.objects.get(app_label__exact=package, model__exact=module)
>>> o_id = Orange.objects.get(weight=10).id
>>> k = cmodels.Comment(target_ct=contenttype, target_id=o_id, content='content on 10kg orange')
>>> k.save()
>>> cmodels.Comment.objects.all()
[<Comment: comment[1] 'comment on ...' on Apple object>, <Comment: comment[2] 'content on ...' on Orange object>]


"""


__test__ = {
    'komments_model' : komments_model,
}


if __name__ == '__main__':
    import doctest
    doctest.testmod()

