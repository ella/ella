# --- doc tests for menu app ---
import logging.config
from settings import *
logging.config.fileConfig(LOGGING_CONFIG_FILE)

menu_simple = """
>>> from django import template
>>> from django.template import Context, Template
>>> from ella.menu.models import Menu, MenuItem
>>> from ella.menu.templatetags.menu import *
>>> tpl = '''
...   {% block container %}
...     {% load menu %}
...     {% menu main-menu %}
...   {% endblock %}
... '''
>>> tpl_lines = tpl.split('\\n')
>>> tpl_lines = map(lambda z: z.strip(), tpl_lines)
>>> tpl = ''.join(tpl_lines)
>>> cx = Context({'context': 'is not important there'})
>>> t = Template(tpl)
>>> t.render(cx)
u'templates/inclusion_tags/menu/main-menu.html template"/Prvni polozka subitems: []""/Druha polozka subitems: [&lt;MenuItem: /Druha polozka/Odkaz na kategorii&gt;, &lt;MenuItem: /Druha polozka/Odkaz ven&gt;]"\\n'

# test non-existing menu slug

>>> tpl = '''
...   {% block container %}
...     {% load menu %}
...     {% menu howghmenu %}
...   {% endblock %}
... '''
>>> tpl_lines = tpl.split('\\n')
>>> tpl_lines = map(lambda z: z.strip(), tpl_lines)
>>> tpl = ''.join(tpl_lines)
>>> cx = Context({'context': 'is not important there'})
>>> t = Template(tpl)
>>> t.render(cx)
u''
"""


menu_for_object = """
>>> from django import template
>>> from django.template import Context, Template
>>> from ella.core.models import Category
>>> from ella.menu.models import Menu, MenuItem
>>> from ella.menu.templatetags.menu import *
>>> tpl = '''
...   {% block container %}
...     {% load menu %}
...     {% menu main-menu for cat %}
...   {% endblock %}
... '''
>>> tpl_lines = tpl.split('\\n')
>>> tpl_lines = map(lambda z: z.strip(), tpl_lines)
>>> tpl = ''.join(tpl_lines)
>>> cat = Category.objects.get(pk=1)
>>> cx = Context({'cat': cat})
>>> t = Template(tpl)
>>> t.render(cx)
u'templates/inclusion_tags/menu/category/homepage/main-menu.html template. "/Prvni polozka subitems: []""/Druha polozka subitems: [&lt;MenuItem: /Druha polozka/Odkaz na kategorii&gt;, &lt;MenuItem: /Druha polozka/Odkaz ven&gt;]"\\n'

>>> m = Menu.objects.get(slug='main-menu')
>>> xcat = Category.objects.get(pk=2)  # try another category for first level
>>> MenuItem.objects.get_level(m, 1, xcat)
[<MenuItem: /Prvni polozka>, <MenuItem: /Druha polozka>]

>>> m = Menu.objects.get(slug='main-menu')
>>> xcat = Category.objects.get(pk=3)  # try another category for first level
>>> MenuItem.objects.get_level(m, 1, xcat)
[<MenuItem: /Prvni polozka>, <MenuItem: /Druha polozka>]


# test non-existing menu slug

>>> tpl = '''
...   {% block container %}
...     {% load menu %}
...     {% menu howgh for cat %}
...   {% endblock %}
... '''
>>> tpl_lines = tpl.split('\\n')
>>> tpl_lines = map(lambda z: z.strip(), tpl_lines)
>>> tpl = ''.join(tpl_lines)
>>> cat = Category.objects.get(pk=1)
>>> cx = Context({'cat': cat})
>>> t = Template(tpl)
>>> t.render(cx)
u''

# test '{% menu xyz for something-not-existing %}'

>>> tpl = '''
...   {% block container %}
...     {% load menu %}
...     {% menu main-menu for badthing %}
...   {% endblock %}
... '''
>>> tpl_lines = tpl.split('\\n')
>>> tpl_lines = map(lambda z: z.strip(), tpl_lines)
>>> tpl = ''.join(tpl_lines)
>>> bad = MenuItem.objects.all()[0]
>>> cx = Context({'badthing': bad})
>>> t = Template(tpl)
>>> try:
...     t.render(cx)
... except TemplateSyntaxError, e:
...     pass
>>> type(e)
<class 'django.template.TemplateSyntaxError'>
>>> unicode(e.message)
u"Object should be instance of Category class. type is <class 'ella.menu.models.MenuItem'>"

# first nested level

>>> cat = Category.objects.get(pk=1)
>>> m = Menu.objects.get(slug='main-menu')
>>> MenuItem.objects.get_level(m, 2, cat)
[<MenuItem: /Druha polozka/Odkaz na kategorii>, <MenuItem: /Druha polozka/Odkaz ven>]

>>> m = Menu.objects.get(slug='main-menu')
>>> xcat = Category.objects.get(pk=2)  # try another category
>>> MenuItem.objects.get_level(m, 2, xcat)
[<MenuItem: /Druha polozka/Odkaz na kategorii>, <MenuItem: /Druha polozka/Odkaz ven>]

>>> m = Menu.objects.get(slug='main-menu')
>>> xcat = Category.objects.get(pk=3)  # try another category
>>> MenuItem.objects.get_level(m, 2, xcat)
[<MenuItem: /Druha polozka/Odkaz na kategorii>, <MenuItem: /Druha polozka/Odkaz ven>]

# second nested level

>>> m = Menu.objects.get(slug='main-menu')
>>> xcat = Category.objects.get(pk=2)  # try another category
>>> MenuItem.objects.get_level(m, 3, xcat)
[<MenuItem: /Druha polozka/Odkaz ven/N2 Odkaz ven>, <MenuItem: /Druha polozka/Odkaz ven/N2 Dalsi odkaz ven>, <MenuItem: /Druha polozka/Odkaz ven/N2 nested category>]

>>> m = Menu.objects.get(slug='main-menu')
>>> xcat = Category.objects.get(pk=3)  # try another category
>>> MenuItem.objects.get_level(m, 3, xcat)
[<MenuItem: /Druha polozka/Odkaz ven/N2 Odkaz ven>, <MenuItem: /Druha polozka/Odkaz ven/N2 Dalsi odkaz ven>, <MenuItem: /Druha polozka/Odkaz ven/N2 nested category>]

# first nested level (temmplate tag)

>>> tpl = '''
...   {% block container %}
...     {% load menu %}
...     {% menu main-menu level 2 for cat %}
...   {% endblock %}
... '''
>>> tpl_lines = tpl.split('\\n')
>>> tpl_lines = map(lambda z: z.strip(), tpl_lines)
>>> tpl = ''.join(tpl_lines)
>>> cx = Context({'cat': cat})
>>> t = Template(tpl)
>>> t.render(cx)
u'templates/inclusion_tags/menu/category/homepage/main-menu.html template. "/Druha polozka/Odkaz na kategorii subitems: []""/Druha polozka/Odkaz ven subitems: [&lt;MenuItem: /Druha polozka/Odkaz ven/N2 Odkaz ven&gt;, &lt;MenuItem: /Druha polozka/Odkaz ven/N2 Dalsi odkaz ven&gt;, &lt;MenuItem: /Druha polozka/Odkaz ven/N2 nested category&gt;]"\\n'
"""

menu_for_generic = """
>>> from django import template
>>> from django.template import Context, Template
>>> from ella.core.models import Category
>>> from ella.menu.models import Menu, MenuItem
>>> from ella.menu.templatetags.menu import *
>>> tpl = '''
...   {% block container %}
...     {% load menu %}
...     {% menu main-menu for category with pk 1 %}
...   {% endblock %}
... '''
>>> tpl_lines = tpl.split('\\n')
>>> tpl_lines = map(lambda z: z.strip(), tpl_lines)
>>> tpl = ''.join(tpl_lines)
>>> cx = Context({})
>>> t = Template(tpl)
>>> t.render(cx)
u'templates/inclusion_tags/menu/category/homepage/main-menu.html template. "/Prvni polozka subitems: []""/Druha polozka subitems: [&lt;MenuItem: /Druha polozka/Odkaz na kategorii&gt;, &lt;MenuItem: /Druha polozka/Odkaz ven&gt;]"\\n'

# multiple filter arguments in tpl tag

>>> tpl = '''
...   {% block container %}
...     {% load menu %}
...     {% menu main-menu for category with pk 1  slug homepage %}
...   {% endblock %}
... '''
>>> tpl_lines = tpl.split('\\n')
>>> tpl_lines = map(lambda z: z.strip(), tpl_lines)
>>> tpl = ''.join(tpl_lines)
>>> cx = Context({})
>>> t = Template(tpl)
>>> t.render(cx)
u'templates/inclusion_tags/menu/category/homepage/main-menu.html template. "/Prvni polozka subitems: []""/Druha polozka subitems: [&lt;MenuItem: /Druha polozka/Odkaz na kategorii&gt;, &lt;MenuItem: /Druha polozka/Odkaz ven&gt;]"\\n'

# level test

>>> tpl = '''
...   {% block container %}
...     {% load menu %}
...     {% menu main-menu level 1 for category with pk 1  slug homepage %}
...   {% endblock %}
... '''
>>> tpl_lines = tpl.split('\\n')
>>> tpl_lines = map(lambda z: z.strip(), tpl_lines)
>>> tpl = ''.join(tpl_lines)
>>> cx = Context({})
>>> t = Template(tpl)
>>> t.render(cx)
u'templates/inclusion_tags/menu/category/homepage/main-menu.html template. "/Prvni polozka subitems: []""/Druha polozka subitems: [&lt;MenuItem: /Druha polozka/Odkaz na kategorii&gt;, &lt;MenuItem: /Druha polozka/Odkaz ven&gt;]"\\n'

>>> tpl = '''
...   {% block container %}
...     {% load menu %}
...     {% menu main-menu level 2 for category with pk 3 %}
...   {% endblock %}
... '''
>>> tpl_lines = tpl.split('\\n')
>>> tpl_lines = map(lambda z: z.strip(), tpl_lines)
>>> tpl = ''.join(tpl_lines)
>>> cx = Context({})
>>> t = Template(tpl)
>>> t.render(cx)
u'templates/inclusion_tags/menu/category/homepage/main-menu.html template. "/Druha polozka/Odkaz na kategorii subitems: []""/Druha polozka/Odkaz ven subitems: [&lt;MenuItem: /Druha polozka/Odkaz ven/N2 Odkaz ven&gt;, &lt;MenuItem: /Druha polozka/Odkaz ven/N2 Dalsi odkaz ven&gt;, &lt;MenuItem: /Druha polozka/Odkaz ven/N2 nested category&gt;]"\\n'

# nonexisting category

>>> tpl = '''
...   {% block container %}
...     {% load menu %}
...     {% menu main-menu for category with slug hegesvaros %}
...   {% endblock %}
... '''
>>> tpl_lines = tpl.split('\\n')
>>> tpl_lines = map(lambda z: z.strip(), tpl_lines)
>>> tpl = ''.join(tpl_lines)
>>> cx = Context({})
>>> t = Template(tpl)
>>> t.render(cx)
u''
"""

highlight = """
>>> from django import template
>>> from django.template import Context, Template
>>> from ella.core.models import Category
>>> from ella.menu.models import Menu, MenuItem
>>> from ella.menu.templatetags.menu import *

# top level highlight

>>> m = Menu.objects.get(slug='main-menu')
>>> cat = Category.objects.get(pk=1)
>>> mis = MenuItem.objects.get_level(m, 1, cat)
>>> map(lambda m: '%s:%s' % (m, hasattr(m, 'mark')), mis)
['/Prvni polozka:False', '/Druha polozka:True']

>>> m = Menu.objects.get(slug='main-menu')
>>> cat = Category.objects.get(pk=2) # highlight when nested category is selected
>>> mis = MenuItem.objects.get_level(m, 1, cat)
>>> map(lambda m: '%s:%s' % (m, hasattr(m, 'mark')), mis)
['/Prvni polozka:False', '/Druha polozka:True']

>>> m = Menu.objects.get(slug='main-menu')
>>> cat = Category.objects.get(pk=3) # highlight when nested category is selected
>>> mis = MenuItem.objects.get_level(m, 1, cat)
>>> map(lambda m: '%s:%s' % (m, hasattr(m, 'mark')), mis)
['/Prvni polozka:False', '/Druha polozka:True']

# first nested level

>>> m = Menu.objects.get(slug='main-menu')
>>> cat = Category.objects.get(pk=2)
>>> mis = MenuItem.objects.get_level(m, 2, cat)
>>> map(lambda m: '%s:%s' % (m, hasattr(m, 'mark')), mis)
['/Druha polozka/Odkaz na kategorii:False', '/Druha polozka/Odkaz ven:True']

>>> m = Menu.objects.get(slug='main-menu')
>>> cat = Category.objects.get(pk=3)
>>> mis = MenuItem.objects.get_level(m, 2, cat)
>>> map(lambda m: '%s:%s' % (m, hasattr(m, 'mark')), mis)
['/Druha polozka/Odkaz na kategorii:False', '/Druha polozka/Odkaz ven:True']

# second nested level

>>> m = Menu.objects.get(slug='main-menu')
>>> cat = Category.objects.get(pk=2) # not enough nested category to highlight menu items
>>> mis = MenuItem.objects.get_level(m, 3, cat)
>>> map(lambda m: '%s:%s' % (m, hasattr(m, 'mark')), mis)
['/Druha polozka/Odkaz ven/N2 Odkaz ven:False', '/Druha polozka/Odkaz ven/N2 Dalsi odkaz ven:False', '/Druha polozka/Odkaz ven/N2 nested category:False']

>>> m = Menu.objects.get(slug='main-menu')
>>> cat = Category.objects.get(pk=3)
>>> mis = MenuItem.objects.get_level(m, 3, cat)
>>> map(lambda m: '%s:%s' % (m, hasattr(m, 'mark')), mis)
['/Druha polozka/Odkaz ven/N2 Odkaz ven:False', '/Druha polozka/Odkaz ven/N2 Dalsi odkaz ven:False', '/Druha polozka/Odkaz ven/N2 nested category:True']

>>> tpl = '''
...   {% block container %}
...     {% load menu %}
...     {% menu main-menu level 2 for category with pk 3 %}
...     SOMETHING SELECTED?
...     {% for i in menu_var %}
...       {% if i.selected_item %}
...         SELECTED "{{i}}"
...       {% endif %}
...     {% endfor %}
...   {% endblock %}
... '''
>>> tpl_lines = tpl.split('\\n')
>>> tpl_lines = map(lambda z: z.strip(), tpl_lines)
>>> tpl = ''.join(tpl_lines)
>>> cx = Context({'category': cat})
>>> t = Template(tpl)
>>> # t.render(cx)
"""

properties_test = """
>>> from ella.core.models import Category
>>> from ella.menu.models import Menu, MenuItem
>>> mi = MenuItem.objects.get(pk=4)
>>> mi.get_slug()
u'homepage'
>>> mi.get_url()
'/'

>>> mi = MenuItem.objects.get(pk=2)
>>> mi.subitems
[<MenuItem: /Druha polozka/Odkaz na kategorii>, <MenuItem: /Druha polozka/Odkaz ven>]
"""

__test__ = {
    'menu_simple': menu_simple,
    'menu_for_object': menu_for_object,
    'menu_for_generic': menu_for_generic,
    'highlight_selected': highlight,
    'properties': properties_test,
}

