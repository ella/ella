base = r'''
>>> from django.template import Template, Context
>>> t = Template("{% load core %}{% box some_type for app_label.model_name with id 1 %}{% endbox %}")
Traceback (most recent call last):
  ...
TemplateSyntaxError: Model u'app_label.model_name' does not exist
>>> t = Template("{% load core %}{% box some_type for box_sample.boxedobject with id 1 %}{% endbox %}")
>>> t.render(Context ({}))
u'box/box_sample.boxedobject/some_type.html\nboxed object 1\n'
'''

templates = r'''
>>> 10
10
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
    'templates' : templates,
    'params' : params,
    'media' : media,
}

if __name__ == '__main__':
    import doctest
    doctest.testmod()

