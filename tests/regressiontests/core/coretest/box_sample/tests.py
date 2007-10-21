base = r'''
>>> from django.template import Template, Context
>>> t = Template("{% box some_type for app_label.model_name with id 1 %}{% endbox %}")

# silently fail
Traceback (most recent call last):
  ...
TemplateSyntaxError: Model u'app_label.model_name' does not exist
>>> t = Template("{% box some_type for box_sample.boxedobject with id 1 %}{% endbox %}")
>>> t.render(Context ({}))
u'box/box_sample.boxedobject/some_type.html\nboxed object 1\n'
>>> t = Template("{% box other_type for box_sample.boxedobject with id 1 %}{% endbox %}")
>>> t.render(Context ({}))
Traceback (most recent call last):
  ...
TemplateSyntaxError: Caught an exception while rendering: box/content_type/box_sample.boxedobject/other_type.html, box/content_type/box_sample.boxedobject/box.html, box/box_sample.boxedobject/other_type.html, box/box_sample.boxedobject/base_box.html
<BLANKLINE>
Original Traceback (most recent call last):
  ...
TemplateDoesNotExist: box/content_type/box_sample.boxedobject/other_type.html, box/content_type/box_sample.boxedobject/box.html, box/box_sample.boxedobject/other_type.html, box/box_sample.boxedobject/base_box.html
<BLANKLINE>
>>> t = Template("{% box other_type for box_sample.unboxedobject with id 2 %}{% endbox %}")
>>> t.render(Context ({}))
u'box/box_sample.unboxedobject/base_box.html\nunboxed object 2\n'
'''

media = r'''
>>> from django.template import Template, Context
>>> t = Template("{% box some_type for box_sample.boxedobject with id 1 %}{% endbox %}{% box_media %}")
>>> t.render(Context())
u'box/box_sample.boxedobject/some_type.html\nboxed object 1\n\n\n\n'


>>> t = Template("""{% box null_box for box_sample.boxedobject with id 1 %}
... js: /some/path_to.js
... {% endbox %}{% box_media %}""")
>>> t.render(Context())
u'\n\n/some/path_to.js\n\n'


>>> t = Template("""{% box null_box for box_sample.boxedobject with id 1 %}
... js: /some/path_to.js
... js: /some/other/path_to.js
... {% endbox %}{% box null_box for box_sample.boxedobject with id 1 %}
... js: /some/path_to.js
... js: /third/path_to.js
... {% endbox %}{% box_media %}""")
>>> t.render(Context())
u'\n\n/some/path_to.js\n/third/path_to.js\n/some/other/path_to.js\n\n'

>>> t = Template("""{% box null_box for box_sample.boxedobject with id 1 %}
... css: /some/path_to.css
... css: /some/other/path_to.css
... {% endbox %}{% box null_box for box_sample.boxedobject with id 1 %}
... css: /some/path_to.css
... css: /third/path_to.css
... {% endbox %}{% box_media %}""")
>>> t.render(Context())
u'\n/third/path_to.css\n/some/other/path_to.css\n/some/path_to.css\n\n\n'
'''


level = r'''
>>> from django.template import Template, Context

# empty level parameter
>>> t = Template("{% box level_test for box_sample.boxedobject with id 1 %}{% endbox %}{% box_media %}")
>>> t.render(Context())
u'level: 1 next_level: 2\n\n\n\n'

# some given value
>>> t = Template("{% box level_test for box_sample.boxedobject with id 1 %}level: 3{% endbox %}{% box_media %}")
>>> t.render(Context())
u'level: 3 next_level: 4\n\n\n\n'

# bogus value that will cause error
>>> t = Template("{% box level_test for box_sample.boxedobject with id 1 %}level: crash{% endbox %}{% box_media %}")
>>> t.render(Context())
u'level: 1 next_level: 2\n\n\n\n'
'''


static = r'''
>>> from django.template import Template, Context

# empty level parameter
>>> t = Template("{% staticbox level_test %}")
>>> t.render(Context())
u'level : 1\nnext_level : 2\n'

>>> t = Template("{% staticbox level_test 2 %}")
>>> t.render(Context())
u'level : 2\nnext_level : 3\n'

>>> t = Template("{% staticbox level_test level %}")
>>> t.render(Context({'level' : 4}))
u'level : 4\nnext_level : 5\n'

>>> t.render(Context())
u'level : 1\nnext_level : 2\n'
'''

__test__ = {
    'base' : base,
    'media' : media,
    'level' : level,
    'static' : static,
}

if __name__ == '__main__':
    import doctest
    doctest.testmod()

