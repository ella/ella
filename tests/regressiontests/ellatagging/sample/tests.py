# --- doc tests for ella.tagging ---
from settings import *

cloud_for_model = r"""
#{{{
>>> from ella.core.models import Category
>>> from ella.tagging.models import *
>>> from sample.models import *
>>> for t in TaggedItem.objects.all():
...     t.delete()
>>> for t in Tag.objects.all():
...     t.delete()

>>> s = Something(title='ahoj', description='te pic')
>>> t = Something(title='ciao', description='neco xyz')
>>> l = IchBinLadin(organisation='johohoo', category=Category.objects.get(pk=2))
>>> s.save(); t.save(); l.save()
>>> Tag.objects.add_tag(l, 'a')
>>> Tag.objects.add_tag(s, 'a')
>>> Tag.objects.add_tag(s, 'b')
>>> Tag.objects.add_tag(t, 'b')

>>> Tag.objects.cloud_for_model(Something)
[<Tag: a>, <Tag: b>]

>>> Tag.objects.cloud_for_model(IchBinLadin)
[<Tag: a>]
""" #}}}

cloud_category = r"""
#{{{
>>> from ella.core.models import Category
>>> from ella.tagging.models import *
>>> from sample.models import *
>>> for t in TaggedItem.objects.all():
...     t.delete()
>>> for t in Tag.objects.all():
...     t.delete()

>>> cat = Category.objects.get(pk=2)
>>> s = IchBinLadin(organisation='johohoo', category=Category.objects.get(pk=3))
>>> t = IchBinLadin(organisation='johohoo', category=cat)
>>> l = IchBinLadin(organisation='johohoo', category=cat)
>>> s.save(); t.save(); l.save()
>>> Tag.objects.add_tag(l, 'ahoj')
>>> Tag.objects.add_tag(l, 'blabla')
>>> Tag.objects.add_tag(s, 'nonono')
>>> Tag.objects.add_tag(s, 'ahoj')
>>> Tag.objects.add_tag(t, 'fireball')
>>> Tag.objects.add_tag(t, 'ahoj')
>>> res = Tag.objects.cloud_for_category(cat)
>>> ls = map(lambda x: x.__unicode__(), res)
>>> ls.sort(); ls
[u'ahoj', u'blabla', u'fireball']
"""#}}}

tag_priority = r"""
#{{{
>>> from ella.core.models import Category
>>> from ella.tagging.models import *
>>> from sample.models import *
>>> for t in TaggedItem.objects.all():
...     t.delete()
>>> for t in Tag.objects.all():
...     t.delete()
"""#}}}


"""
TODO TESTY:
1. otestovat stezenjni funkcionalitu (tag cloud)
2. tagy v dvou urovnich priority
3. naseptavac
4. tagy v kategoriich
"""

__test__ = {
    'ellatagging_cloud': cloud_for_model,
    'ellatagging_category': cloud_category,
}
