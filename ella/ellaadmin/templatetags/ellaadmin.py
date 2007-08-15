
from django import template
from django.contrib.contenttypes.models import ContentType
from django.contrib import admin
from django.utils import simplejson

REG_CT_LIST = [ ContentType.objects.get_for_model(i) for i in admin.site._registry ]
REG_CT_DICT = dict([ (i.id, '%s/%s' % (i.app_label, i.model)) for i in REG_CT_LIST ])
REG_CT_JSON = simplejson.dumps(REG_CT_DICT, indent=2)
REG_CT_VARNAME = 'paths'

REG_CT_HTML = """
<script type='text/javascript'>
<![CDATA[
%s = %s
]]>
</script>""" % (REG_CT_VARNAME, REG_CT_JSON)


register = template.Library()

class InsertModels(template.Node):
    def render(self, context):
        return REG_CT_HTML

@register.tag
def insert_admin_apps(parser, token):
    return InsertModels()

