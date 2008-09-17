base =  r"""
>>> from django.template import Template, Context

>>> from common.attachments.models import Attachment

is db really empty?

>>> Attachment.objects.all()
[]

load test data

>>> from django.core.management import call_command
>>> call_command('loaddata', 'attachments_test_data', verbosity=False)

do some tests

>>> attachment_1 = Attachment.objects.get(pk=1)
>>> attachment_2 = Attachment.objects.get(pk=2)

>>> attachment_1, attachment_2
(<Attachment: some picture>, <Attachment: some text>)

>>> c = Context({'attachment_1': attachment_1, 'attachment_2': attachment_2})
>>> t = Template((
... '{% box test_link for attachment_1 %}{% endbox %}'
... '{% box test_link for attachment_2 %}{% endbox %}'
...))
>>> print t.render(c).strip()
<a href="/static/attach/2008/09/03/picture.png"><img src="/static/attach/2008/09/03/picture.png" title="some picture" /></a>
<a href="/static/attach/2008/09/03/text.txt">some text</a>


"""

__test__ = {
    'base': base,
}

