adverts = r'''
>>> from django import template
>>> t=template.Template('{%load adverts %}{% advert %}')
>>> t.render(template.Context({}))
u'<!-- AD MISSING SERVER/SECTION (null)/(null) -->'
>>> t=template.Template('{%load adverts %}{% advert type "aaa" %}')
>>> t.render(template.Context({}))
u''
>>> t=template.Template('{%load adverts %}{% advert type aaa %}')
>>> t.render(template.Context({}))
u'<!-- AD MISSING SERVER/SECTION (null)/(null) -->'
>>> t.render(template.Context({'aaa':123}))
u'<!-- AD MISSING SERVER/SECTION (null)/(null) -->'
>>> t=template.Template('{%load adverts %}{% advert type %}')
Traceback (most recent call last):
...
TemplateSyntaxError: u'advert' tag requires even number of arguments
>>> t=template.Template('{%load adverts %}{% advert unknown_parameter "aaa" %}')
Traceback (most recent call last):
    ...
TemplateSyntaxError: advert tag does not accept 'unknown_parameter' parameter
>>> t=template.Template('{%load adverts %}{% advert section "hp" size "standard" place "sky" server "zdravi" %}')
>>> t.render(template.Context({}))
u'<!-- AD MISSING SERVER/SECTION (null)/(null) -->'
'''

backend_srv = """
>>> from nc.backendserver import *
>>> 123
123
"""

__test__ = {
    'adverts' : adverts,
    'backend_server': backend_srv,
}

if __name__ == '__main__':
    import doctest
    doctest.testmod()

