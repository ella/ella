base = r'''
>>> from django.template import Template, Context
>>> t = Template("{% load core %}{% box some_type for app_label.model_name with id 1 %}{% endbox %}")
Traceback (most recent call last):
  ...
TemplateSyntaxError: Model u'app_label.model_name' does not exist
>>> t = Template("{% load core %}{% box some_type for box_sample.boxedobject with id 1 %}{% endbox %}")
>>> t.render(Context ({}))
u'box/box_sample.boxedobject/some_type.html\nboxed object 1\n'
>>> t = Template("{% load core %}{% box other_type for box_sample.boxedobject with id 1 %}{% endbox %}")
>>> t.render(Context ({}))
Traceback (most recent call last):
  ...
TemplateSyntaxError: Caught an exception while rendering: box/box_sample.boxedobject/other_type.html, box/box_sample.boxedobject/base_box.html
<BLANKLINE>
Original Traceback (most recent call last):
  ...
TemplateDoesNotExist: box/box_sample.boxedobject/other_type.html, box/box_sample.boxedobject/base_box.html
<BLANKLINE>
>>> t = Template("{% load core %}{% box other_type for box_sample.unboxedobject with id 2 %}{% endbox %}")
>>> t.render(Context ({}))
u'box/box_sample.unboxedobject/base_box.html\nunboxed object 2\n'
'''

params = r'''
>>> 11
11
'''

media = r'''
>>> 111
111
'''

__test__ = {
    'base' : base,
    'params' : params,
    'media' : media,
}

if __name__ == '__main__':
    import doctest
    doctest.testmod()

