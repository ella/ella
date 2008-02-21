
positions_template_tag = r"""
>>> from django.template import Template, Context
>>> from ella.core.models import Category

>>> c1 = Category.objects.get(title='homepage')
>>> c2 = Category.objects.get(title='first category')

>>> c = Context({'category': c2,})

>>> t = Template('''{% spaceless %}
... {% load positions %}
... {% positions for category,homepage as a %}
... {% if a.featured_one or a.featured_two or a.featured_three %}
... {{a.featured_one}},
... {{a.featured_two}},
... {{a.featured_three}},
... {% endif %}
... {% endspaceless %}''')
>>> t.render(c)
u'example.com/first-category:featured_one,\nexample.com/first-category:featured_two,\nexample.com/:featured_three,'

>>> t = Template('''{% spaceless %}
... {% load positions %}
... {% positions for category as active_positions %}
... {{active_positions.featured_one}},
... {{active_positions.featured_two}},
... {{active_positions.featured_three}},
... {% endspaceless %}''')
>>> t.render(c)
u'example.com/first-category:featured_one,\nexample.com/first-category:featured_two,\n,'

>>> t = Template('''{% spaceless %}
... {% load positions %}
... {% positions for category as active_positions %}
... {{active_positions.featured_one.target}}
... {% endspaceless %}''')
>>> t.render(c)
u'admin'


TODO:
* handle category names "some nice name of category"
* handle position names "some-nice-name-of-position"

"""

__test__ = {
    'positions_template_tag': positions_template_tag,
}


if __name__ == '__main__':
    import doctest
    doctest.testmod()

