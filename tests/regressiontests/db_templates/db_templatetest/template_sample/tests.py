base = r'''
>>> from ella.db_templates import models
>>> t = models.DbTemplate.objects.get(name="database.html")
>>> t.save()
>>> t.text
u'{% extends "base.html" %}{% block main %}database.html\n{% endblock %}'

>>> from django.template import loader, Context
>>> temp = loader.get_template("disk.html")
>>> temp.render(Context())
u'disk - templates/base.html\n\ndisk.html\n\n'

>>> temp = loader.get_template("database.html")
>>> temp.render(Context())
u'disk - templates/base.html\ndatabase.html\n\n'

>>> models.DbTemplate.objects.get(name="database_block.html").save()
>>> source, origin = loader.find_template_source("database_block.html")
>>> source
u'{% extends "base.html" %}{% block main %}{% box box_type for auth.permission with id 1 %}param1:value1\nparam2:value2\n{% endbox %}{% endblock %}'

>>> temp = loader.get_template("database_block.html")
>>> temp.render(Context())
u'disk - templates/base.html\nauth | message | Can add message\n\n'
'''

__test__ = {
    'base' : base,
}

if __name__ == '__main__':
    import doctest
    doctest.testmod()


