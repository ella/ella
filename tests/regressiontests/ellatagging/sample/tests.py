# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
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
>>> ti, created = Tag.objects.add_tag(l, 'a')
>>> ti, created = Tag.objects.add_tag(s, 'a')
>>> ti, created = Tag.objects.add_tag(s, 'b')
>>> ti, created = Tag.objects.add_tag(t, 'b')

>>> Tag.objects.cloud_for_model(Something)
[<Tag: a>, <Tag: b>]

>>> Tag.objects.cloud_for_model(IchBinLadin)
[<Tag: a>]
>>> #}}}
"""

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
>>> cat is None
False

>>> s = IchBinLadin(organisation='johohoo', category=Category.objects.get(pk=3))
>>> t = IchBinLadin(organisation='vachler art', category=cat)
>>> l = IchBinLadin(organisation='santa cruz aupair', category=cat)
>>> m = IchBinLadin(organisation='co to e', category=cat)
>>> s.save(); t.save(); l.save(); m.save()
>>> ti, created = Tag.objects.add_tag(l, 'ahoj')
>>> ti, created = Tag.objects.add_tag(l, 'blabla')
>>> ti, created = Tag.objects.add_tag(s, 'nonono')
>>> ti, created = Tag.objects.add_tag(s, 'ahoj')
>>> ti, created = Tag.objects.add_tag(t, 'fireball')
>>> ti, created = Tag.objects.add_tag(t, 'fireball')
>>> ti, created = Tag.objects.add_tag(t, 'fireball')
>>> ti, created = Tag.objects.add_tag(t, 'ahoj')
>>> ti, created = Tag.objects.add_tag(m, 'ahoj')
>>> ti, created = Tag.objects.add_tag(m, 'blabla')

>>> cat is None
False

>>> res = Tag.objects.cloud_for_category(cat)  # all tags in category (priority independent)
>>> res
[<Tag: ahoj>, <Tag: blabla>, <Tag: fireball>]

>>> map(lambda x: x.count, res)
[3, 2, 1]
>>> #}}}
"""

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
>>> ti, created = Tag.objects.add_tag(l, 'ahoj')
>>> ti, created = Tag.objects.add_tag(l, 'blabla', SECONDARY_TAG)
>>> ti, created = Tag.objects.add_tag(s, 'nonono')
>>> ti, created = Tag.objects.add_tag(s, 'ahoj')
>>> ti, created = Tag.objects.add_tag(t, u'ěščřžýáíé', SECONDARY_TAG)
>>> ti, created = Tag.objects.add_tag(t, u'ěščřžýáíé')
>>> ti, created = Tag.objects.add_tag(m, 'ahoj')
>>> ti, created = Tag.objects.add_tag(m, 'blabla', SECONDARY_TAG)
>>> Tag.objects.cloud_for_category(cat, priority=SECONDARY_TAG)
[<Tag: blabla>, <Tag: ěščřžýáíé>]

>>> Tag.objects.cloud_for_category(cat, priority=PRIMARY_TAG)
[<Tag: ahoj>, <Tag: ěščřžýáíé>]
>>> #}}}
"""

suggester_response = r"""
#{{{
>>> from ella.tagging.utils import PRIMARY_TAG, SECONDARY_TAG
>>> from ella.tagging.models import *
>>> from sample.models import *
>>> for t in TaggedItem.objects.all():
...     t.delete()
>>> for t in Tag.objects.all():
...     t.delete()

>>> cat = Category.objects.get(pk=2)
>>> l = IchBinLadin(organisation='santa cruz aupairation', category=cat)
>>> l.save()
>>> ti, created = Tag.objects.add_tag(l, 'ahoj')
>>> ti, created = Tag.objects.add_tag(l, 'nazdar')
>>> ti, created = Tag.objects.add_tag(l, 'dvou slovny')
>>> ti, created = Tag.objects.add_tag(l, u'\xec\xb9\xe8\xf8\xbe\xfd\xe1\xed')
>>> ti, created = Tag.objects.add_tag(l, u'\xb9la \xb9\xe1\xb9e\xf2 po most\xec')

>>> from django.test.client import Client
>>> from urllib import quote
>>> cli = Client();


>>> # simple one word tags:
>>> res = cli.get('/t/', {'q': 'šla'})
>>> res.status_code
200
>>> res.content == u'\xb9la \xb9\xe1\xb9e\xf2 po most\xec'
True

>>> res = cli.get('/t/', {'q': u'\xec\xb9\xe8'})
>>> res.status_code
200
>>> res.content
u'\xec\xb9\xe8\xf8\xbe\xfd\xe1\xed'

>>> res = cli.get('/t/', {'q': 'na'})
>>> res.status_code
200
>>> res.content
'nazdar'

>>> # two word tag
>>> res = cli.get('/t/', {'q': 'dvo'})
>>> res.status_code
200
>>> res.content
'dvou slovny'
>>> #}}}
"""

# TODO test also saving data from the form (deletin' and savin' tags)
options_test = """
>>> from ella.core.models import Category
>>> from django.contrib import admin
>>> from ella.tagging.admin import TagInlineFormset, TaggingInlineOptions
>>> from sample.models import *
>>> from django.utils.datastructures import MultiValueDict
>>> empty_data = MultiValueDict({
...     "tagged_item_-TOTAL_FORMS": ["2"],
...     "tagged_item_-INITIAL_FORMS": ["2"],
...     "tagged_item_-0-tag": ["ahoj"],
...     "tagged_item_-0-priority": [100],
...     "tagged_item_-0-id": [""],
...     "tagged_item_-1-tag": ["ahoj"],
...     "tagged_item_-1-priority": [90],
...     "tagged_item_-1-id": [""]
...})
>>> cat = Category.objects.get(pk=2)
>>> l = IchBinLadin(organisation='santa cruz aupairation', category=cat)
>>> l.save()
>>> opts = TaggingInlineOptions(IchBinLadin, admin.site)
>>> fset_cls = opts.get_formset(None)
>>> fset = fset_cls(data=empty_data, files={}, instance=l)
>>> fset.is_valid()
True
>>> fset.cleaned_data
[{'priority': 100, 'tag': [<Tag: ahoj>], 'id': None}, {'priority': 90, 'tag': [<Tag: ahoj>], 'id': None}]


>>> empty_data = MultiValueDict({
...     "tagged_item_-TOTAL_FORMS": ["2"],
...     "tagged_item_-INITIAL_FORMS": ["2"],
...     "tagged_item_-0-tag": ["ahoj, nazdar, hulahop"],
...     "tagged_item_-0-priority": [100],
...     "tagged_item_-0-id": [""],
...     "tagged_item_-1-tag": ["ahoj"],
...     "tagged_item_-1-priority": [90],
...     "tagged_item_-1-id": [""]
...})
>>> fset = fset_cls(data=empty_data, files={}, instance=l)
>>> fset.is_valid()
True
>>> fset.cleaned_data
[{'priority': 100, 'tag': [<Tag: ahoj>, <Tag: nazdar>, <Tag: hulahop>], 'id': None}, {'priority': 90, 'tag': [<Tag: ahoj>], 'id': None}]



>>> empty_data = MultiValueDict({
...     "tagged_item_-TOTAL_FORMS": ["2"],
...     "tagged_item_-INITIAL_FORMS": ["2"],
...     "tagged_item_-0-tag": ["nazdar"],
...     "tagged_item_-0-priority": [100],
...     "tagged_item_-0-id": [""],
...     "tagged_item_-1-tag": ["ahoj"],
...     "tagged_item_-1-priority": [90],
...     "tagged_item_-1-id": [""]
...})
>>> fset = fset_cls(data=empty_data, files={}, instance=l)
>>> fset.is_valid()
True
>>> fset.cleaned_data
[{'priority': 100, 'tag': [<Tag: nazdar>], 'id': None}, {'priority': 90, 'tag': [<Tag: ahoj>], 'id': None}]
"""


cloud_category_tag = """
>>> from django import template
>>> from django.template import Context, Template
>>> from django.contrib.contenttypes.models import ContentType
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
>>> ti, created = Tag.objects.add_tag(l, 'ahoj')
>>> ti, created = Tag.objects.add_tag(l, 'blabla')
>>> ti, created = Tag.objects.add_tag(s, 'nonono')
>>> ti, created = Tag.objects.add_tag(s, 'ahoj')
>>> ti, created = Tag.objects.add_tag(t, 'fireball')
>>> ti, created = Tag.objects.add_tag(t, 'fireball')
>>> ti, created = Tag.objects.add_tag(t, 'fireball')
>>> ti, created = Tag.objects.add_tag(t, 'ahoj')
>>> ti, created = Tag.objects.add_tag(m, 'ahoj')
>>> ti, created = Tag.objects.add_tag(m, 'blabla')
>>> res = Tag.objects.cloud_for_category(cat)  # all tags in category (priority independent)

>>> tpl = '''
...   {% block container %}
...     {% load tagging %}
...     {% tag_cloud_for_category "first-category" as cloud %}
...     {% for tag in cloud %}
...         "{{tag}}:{{tag.count}}"
...     {% endfor %}
...   {% endblock %}
... '''
>>> tpl_lines = tpl.split('\\n')
>>> tpl_lines = map(lambda z: z.strip(), tpl_lines)
>>> tpl = ''.join(tpl_lines)
>>> t = Template(tpl)
>>> cx = Context({'category': cat})
>>> t.render(cx)
u'"ahoj:3""blabla:2""fireball:1"'

>>> tpl = '''
...   {% block container %}
...     {% load tagging %}
...     {% tag_cloud_for_category "first-category" as cloud with priority=PRIMARY_TAG %}
...     {% for tag in cloud %}
...         "{{tag}}:{{tag.count}}"
...     {% endfor %}
...   {% endblock %}
... '''
>>> tpl_lines = tpl.split('\\n')
>>> tpl_lines = map(lambda z: z.strip(), tpl_lines)
>>> tpl = ''.join(tpl_lines)
>>> t = Template(tpl)
>>> cx = Context({'category': cat})
>>> t.render(cx)
u'"ahoj:3""blabla:2""fireball:1"'
"""


category_from_tpl_var_test = """
>>> from django import template
>>> from django.template import Context, Template
>>> from ella.core.models import Category
>>> from ella.tagging.templatetags.tagging import category_from_tpl_var
>>> cat = Category.objects.get(pk=2)
>>> cx = Context({'category': cat})
>>> category_from_tpl_var('category', cx)
<Category: example.com/first-category>

# return category by slug

>>> category_from_tpl_var('"first-category"', cx)
<Category: example.com/first-category>
"""


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
    #'ellatagging_priority': tag_priority,
    #'ellatagging_suggester': suggester_response,
    'ellatagging_admin_options': options_test,
    'ellatagging_category_from_tpl_var': category_from_tpl_var_test,
    'ellatagging_cloud_for_category_tpltag': cloud_category_tag,
}
