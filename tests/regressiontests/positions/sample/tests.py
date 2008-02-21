
positions_template_tag = r"""
>>> from django.template import Template, Context
>>> from ella.core.models import Category
>>> from ella.positions.models import Position

>>> c1 = Category.objects.get(title='homepage')
>>> c2 = Category.objects.get(title='first category')

>>> c = Context({'category': c2,})

render with and withou fallback
-------------------------------

>>> t = Template('''{% spaceless %}
... {% load positions %}
... {% positions for category,homepage as a %}
... {% if a.featured_one or a.featured_two or a.featured_three %}
... {{a.featured_one}},
... {{a.featured_two}},
... {{a.featured_three}},
... {% endif %}
... {% endspaceless %}''')
>>> print t.render(c)
example.com/first-category:featured_one,
example.com/first-category:featured_two,
example.com/:featured_three,

>>> t = Template('''{% spaceless %}
... {% load positions %}
... {% positions for category as active_positions %}
... {{active_positions.featured_one}},
... {{active_positions.featured_two}},
... {{active_positions.featured_three}},
... {% endspaceless %}''')
>>> print t.render(c)
example.com/first-category:featured_one,
example.com/first-category:featured_two,
,

>>> t = Template('''{% spaceless %}
... {% load positions %}
... {% positions for category as active_positions %}
... {{active_positions.featured_one.target}}
... {% endspaceless %}''')
>>> t.render(c)
u'admin'

render default box
------------------

>>> t = Template('''{% spaceless %}
... {% load positions %}
... {% positions for category as active_positions %}
... {% box featured_one for active_positions.featured_one %}
... css_class:css_class
... {% endbox %}
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


TODO:
* handle category names "some nice name of category"
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

