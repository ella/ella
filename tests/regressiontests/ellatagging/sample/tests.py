# --- doc tests for ella.tagging ---
from settings import *

cloud_for_model = r"""
>>> from ella.tagging.models import *
>>> from sample.models import *
>>> s = Something(title='ahoj', description='te pic')
>>> t = Something(title='ciao', description='neco xyz')
>>> l = IchBinLadin(organisation='johohoo')
>>> s.save(); t.save(); l.save()
>>> Tag.objects.add_tag(l, 'a')
>>> Tag.objects.add_tag(s, 'a')
>>> Tag.objects.add_tag(s, 'b')
>>> Tag.objects.add_tag(t, 'b')

>>> Tag.objects.cloud_for_model(Something)
[<Tag: a>, <Tag: b>]

>>> Tag.objects.cloud_for_model(IchBinLadin)
[<Tag: a>]
"""

"""
TODO TESTY:
1. otestovat stezenjni funkcionalitu (tag cloud)
2. tagy v dvou urovnich priority
3. naseptavac

- vzit ze stareho django tagging
  pouze modely + nase upravy
- priority TaggedItem
- tag cloud per category
- naseptavac
- common.urls -> tagging.views
"""

__test__ = {
    'ellatagging_cloud': cloud_for_model,
}
