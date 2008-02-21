
positions_template_tag = r"""
>>> from django.template import Template, Context
>>> from ella.core.models import Category
>>> from ella.positions.models import Position

>>> c1 = Category.objects.get(title='homepage')
>>> c2 = Category.objects.get(title='first category')

>>> c = Context({'category': c2,})

render with and without fallback
-------------------------------
override box_type in template
-----------------------------

>>> t = Template('''{% spaceless %}
... {% load positions %}
... {% position featured_one for category %}{% endposition %}
... {% position featured_two for category using db %}{% endposition %}
... {% position featured_three for category %}{% endposition %}
... {% endspaceless %}''')
>>> print t.render(c)
<p class="base ">admin</p><p class="db ">admin</p><p class="base ">admin</p>


TODO:
* handle position names "some-nice-name-of-position"

"""

position_template_tag = r"""
>>> from django.template import Template, Context
>>> from ella.core.models import Category
>>> from ella.positions.models import Position

>>> c1 = Category.objects.get(title='homepage')
>>> c2 = Category.objects.get(title='first category')

>>> c = Context({'category': c2,})

render default box
------------------

>>> t = Template('''{% spaceless %}
... {% load positions %}
... {% position featured_one for category using featured_one %}
... css_class:css_class
... {% endposition %}
... {% endspaceless %}''')
>>> t.render(c)
u'<p class="base css_class">admin</p>'

override box_type in db
-----------------------

>>> p = Position.objects.get(name='featured_one')
>>> p.box_type = 'db'
>>> p.text = 'css_class:db_css_class'
>>> p.save()
>>> t.render(c)
u'<p class="db db_css_class">admin</p>'

"""


__test__ = {
    'positions_template_tag': positions_template_tag,
#    'position_template_tag': position_template_tag,
}


if __name__ == '__main__':
    import doctest
    doctest.testmod()

