adverts = r'''
>>> from django import template
>>> t=template.Template('{%load adverts %}{% advert %}')
>>> t.render(template.Context({}))
u'<advert >'
>>> t=template.Template('{%load adverts %}{% advert type "aaa" %}')
>>> t.render(template.Context({}))
u'<advert type="aaa">'
>>> t=template.Template('{%load adverts %}{% advert type aaa %}')
>>> t.render(template.Context({}))
u'<advert type="">'
>>> t.render(template.Context({'aaa':123}))
u'<advert type="123">'
>>> t=template.Template('{%load adverts %}{% advert type %}')
Traceback (most recent call last):
...
TemplateSyntaxError: u'advert' tag requires even number of arguments
>>> t=template.Template('{%load adverts %}{% advert unknown_parameter "aaa" %}')
Traceback (most recent call last):
...
TemplateSyntaxError: advert tag does not accept u'unknown_parameter' parameter
'''

__test__ = {
    'adverts' : adverts,
}

if __name__ == '__main__':
    import doctest
    doctest.testmod()

