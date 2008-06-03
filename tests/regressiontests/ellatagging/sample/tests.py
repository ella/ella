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
>>> t = SomethingElse(title='ciao', description='neco xyz')
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
>>> import ella.tagging.utils
>>> from ella.core.models import Category
>>> from ella.tagging.models import *
>>> from sample.models import *
>>> for t in TaggedItem.objects.all():
...     t.delete()
>>> for t in Tag.objects.all():
...     t.delete()

>>> cat = Category.objects.get(pk=2)
>>> s = IchBinLadin(organisation='johohoo', category=Category.objects.get(pk=3))
>>> t = IchBinLadin(organisation='vachler art', category=cat)
>>> l = IchBinLadin(organisation='santa cruz aupair', category=cat)
>>> m = IchBinLadin(organisation='co to e', category=cat)
>>> s.save(); t.save(); l.save(); m.save()
>>> Tag.objects.add_tag(l, 'ahoj')
>>> Tag.objects.add_tag(l, 'blabla')
>>> Tag.objects.add_tag(s, 'nonono')
>>> Tag.objects.add_tag(s, 'ahoj')
>>> Tag.objects.add_tag(t, 'fireball')
>>> Tag.objects.add_tag(t, 'fireball')
>>> Tag.objects.add_tag(t, 'fireball')
>>> Tag.objects.add_tag(t, 'ahoj')
>>> Tag.objects.add_tag(m, 'ahoj')
>>> Tag.objects.add_tag(m, 'blabla')
>>> res = Tag.objects.cloud_for_category(cat)  # all tags in category (priority independent)
>>> res
[<Tag: ahoj>, <Tag: blabla>, <Tag: fireball>]

>>> map(lambda x: x.count, res)
[3, 2, 1]
"""#}}}

tag_priority = r"""
#{{{
>>> from ella.tagging.utils import PRIMARY_TAG, SECONDARY_TAG
>>> from ella.core.models import Category
>>> from ella.tagging.models import *
>>> from sample.models import *
>>> for t in TaggedItem.objects.all():
...     t.delete()
>>> for t in Tag.objects.all():
...     t.delete()

>>> cat = Category.objects.get(pk=2)
>>> s = IchBinLadin(organisation='johohoo', category=Category.objects.get(pk=3))
>>> t = IchBinLadin(organisation='vachler art', category=cat)
>>> l = IchBinLadin(organisation='santa cruz aupairation', category=cat)
>>> m = IchBinLadin(organisation='co to e', category=cat)
>>> s.save(); t.save(); l.save(); m.save()
>>> Tag.objects.add_tag(l, 'ahoj')
>>> Tag.objects.add_tag(l, 'blabla', SECONDARY_TAG)
>>> Tag.objects.add_tag(s, 'nonono')
>>> Tag.objects.add_tag(s, 'ahoj')
>>> Tag.objects.add_tag(t, 'ěščřžýáíé', SECONDARY_TAG)
>>> Tag.objects.add_tag(t, 'ěščřžýáíé')
>>> Tag.objects.add_tag(m, 'ahoj')
>>> Tag.objects.add_tag(m, 'blabla', SECONDARY_TAG)
>>> Tag.objects.cloud_for_category(cat, priority=SECONDARY_TAG)
[<Tag: blabla>, <Tag: ěščřžýáíé>]

>>> Tag.objects.cloud_for_category(cat, priority=PRIMARY_TAG)
[<Tag: ahoj>, <Tag: ěščřžýáíé>]
"""#}}}


"""
TODO TESTY:
1. otestovat stezenjni funkcionalitu (tag cloud)
2. tagy v dvou urovnich priority
3. naseptavac
4. tagy v kategoriich
"""

__test__ = {
    'ellatagging_cloud': cloud_for_model, # deleted functionality
    'ellatagging_category': cloud_category,
    'ellatagging_priority': tag_priority,
}
