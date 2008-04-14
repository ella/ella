ct_correction = r"""
change TemplateBlock ContentType foreign key
--------------------------------------------

>>> from django.contrib.contenttypes.models import ContentType
>>> from django.contrib.auth.models import Permission
>>> from ella.db_templates.models import TemplateBlock

>>> permission_ct = ContentType.objects.get_for_model(Permission)
>>> for i in TemplateBlock.objects.filter(target_ct__id=4):
...     i.target_ct
...     i.target_ct = permission_ct
...     i.save()
...     i.target_ct
<ContentType: user>
<ContentType: permission>
"""

base = r"""
>>> from ella.db_templates import models
>>> t = models.DbTemplate.objects.get(name="database.html")
>>> t.get_text()
u'{% extends "base.html" %}\n\n{% block main %}\ndatabase.html\n{% endblock %}\n\n{% comment %}\nname: database.html\nsite: example.com\ndescription: Sample template stored in database\n{% endcomment %}\n'

>>> from django.template import loader, Context
>>> temp = loader.get_template("disk.html")
>>> temp.render(Context())
u'disk - templates/base.html\n\ndisk.html\n\n'

>>> temp = loader.get_template("database.html")
>>> temp.render(Context())
u'disk - templates/base.html\n\ndatabase.html\n\n'

>>> models.DbTemplate.objects.get(name="database_block.html").save()

>>> source, origin = loader.find_template_source("database_block.html")
>>> source
u'{% extends "base.html" %}\n\n{% block main %}\n{% box box_type for auth.permission with id 1 %}\nparam1:value1\nparam2:value2\n{% endbox %}\n{% endblock %}\n\n{% comment %}\nname: database_block.html\nsite: example.com\ndescription: Sample template stored in database with boxes\n{% endcomment %}\n'

>>> temp = loader.get_template("database_block.html")
>>> temp.render(Context())
u'disk - templates/base.html\n\nadmin | log entry | Can add log entry\n\n\n'
"""

load = r"""
>>> from ella.db_templates import models
>>> from django.template import Template

TemplateBlock test
------------------
>>> template_string = u'{% extends "base.html" %}{% block main %}database.html\n{% endblock %}'
>>> template_string += '\n\n' + u'{% block box %}\n{% box box_type for auth.permission with id 1 %}param1:value1\r\nparam2:value2\r\n{% endbox %}\n\n{% endblock %}'

# TODO: pridat dobrou reprezentaci BoxNode a vrazit sem do testu
>>> blocks = models.get_blocks(Template(template_string).nodelist[0].nodelist)
>>> (type(blocks[0]['node']), blocks[0]['source'], blocks[0]['name'])
(<class 'django.template.loader_tags.BlockNode'>, u'database.html\n', u'main')
>>> (type(blocks[1]['node']), blocks[1]['source'], blocks[1]['name'])
(<class 'django.template.loader_tags.BlockNode'>, u'\n{% box box_type for auth.permission with id 1 %}param1:value1\r\nparam2:value2\r\n{% endbox %}\n\n', u'box')

>>> box_source = blocks[1]['source']
>>> box_source
u'\n{% box box_type for auth.permission with id 1 %}param1:value1\r\nparam2:value2\r\n{% endbox %}\n\n'

>>> models.TemplateBlock.objects.count()
2
>>> template = models.TemplateBlock.objects.all()[0]
>>> models.TemplateBlock.objects.create_from_string(template, box_source, 'box')
<TemplateBlock: box>
>>> models.TemplateBlock.objects.count()
3

# box options are saved into text
>>> block = models.TemplateBlock.objects.create_from_string(template, '{% box box_type for auth.permission with id 1 %}param1:next_level\r\nparam2:value2\r\n{% endbox %}', 'box2')
>>> block.text
u'param1:next_level\r\nparam2:value2\r\n'

# but it can be compiled template
>>> block = models.TemplateBlock.objects.create_from_string(template, '{% box box_type for auth.permission with id 1 %}param1:{{next_level}}\r\nparam2:value2\r\n{% endbox %}', 'box3')
>>> block.text
u'param1:{{next_level}}\r\nparam2:value2\r\n'

DbTemplate test
---------------
>>> template_string = u'{% extends "base.html" %}{% block main %}database.html\n{% endblock %}'

>>> models.DbTemplate.objects.create_from_string('', 'name.html')
Traceback (most recent call last):
    ...
InvalidTemplate: template without nodes

>>> models.DbTemplate.objects.create_from_string('template', 'name.html')
Traceback (most recent call last):
    ...
InvalidTemplate: template without extends

>>> models.DbTemplate.objects.count()
2
>>> models.TemplateBlock.objects.count()
5
>>> template = models.DbTemplate.objects.create_from_string(template_string, 'name.html')
>>> template
<DbTemplate: name.html>
>>> models.DbTemplate.objects.count()
3
>>> models.TemplateBlock.objects.count()
6

dump and load
-------------
>>> db_template = models.DbTemplate.objects.get(name='name.html')
>>> template_dump = db_template.get_text()
>>> db_template.delete()
>>> db_template = models.DbTemplate.objects.create_from_string(template_dump, 'name.html')
>>> template_dump == db_template.get_text()
True
"""


__test__ = {
    'all': ct_correction + base + load,
}

