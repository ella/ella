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
u'templates/inclusion_tags/menu/main-menu.html template"Prvni polozka subitems: []""Druha polozka subitems: [&lt;MenuItem: Odkaz na kategorii&gt;, &lt;MenuItem: Odkaz ven&gt;]"\\n'

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
u'templates/inclusion_tags/menu/category/homepage/main-menu.html template. "Prvni polozka subitems: []""Druha polozka subitems: [&lt;MenuItem: Odkaz na kategorii&gt;, &lt;MenuItem: Odkaz ven&gt;]"\\n'

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
...     e
TemplateSyntaxError("Object should be instance of Category class. type is <class 'ella.menu.models.MenuItem'>",)
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
u'templates/inclusion_tags/menu/category/homepage/main-menu.html template. "Prvni polozka subitems: []""Druha polozka subitems: [&lt;MenuItem: Odkaz na kategorii&gt;, &lt;MenuItem: Odkaz ven&gt;]"\\n'

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
u'templates/inclusion_tags/menu/category/homepage/main-menu.html template. "Prvni polozka subitems: []""Druha polozka subitems: [&lt;MenuItem: Odkaz na kategorii&gt;, &lt;MenuItem: Odkaz ven&gt;]"\\n'

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
>>> tpl = '''
...   {% block container %}
...     {% load menu %}
...     {% menu main-menu for category with pk 1 %}
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
>>> cat = Category.objects.get(pk=1)
>>> cx = Context({'category': cat})
>>> t = Template(tpl)
>>> t.render(cx)
u'templates/inclusion_tags/menu/category/homepage/main-menu.html template. "Prvni polozka subitems: []""Druha polozka subitems: [&lt;MenuItem: Odkaz na kategorii&gt;, &lt;MenuItem: Odkaz ven&gt;]"\\nSOMETHING SELECTED?SELECTED "Druha polozka"'
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
[<MenuItem: Odkaz na kategorii>, <MenuItem: Odkaz ven>]
"""

__test__ = {
    'menu_simple': menu_simple,
    'menu_for_object': menu_for_object,
    'menu_for_generic': menu_for_generic,
    'highlight_selected': highlight,
    'properties': properties_test,
}

