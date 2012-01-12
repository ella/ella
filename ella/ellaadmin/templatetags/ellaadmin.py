from django import template
from django.contrib.contenttypes.models import ContentType
from django.contrib import admin
from django.utils import simplejson

REG_CT_LIST = [ ContentType.objects.get_for_model(i) for i in admin.site._registry ]
REG_CT_DICT = dict([ (i.id, {'name': i.name, 'path': '%s.%s' % (i.app_label, i.model)}) for i in REG_CT_LIST ])
REG_CT_JSON = simplejson.dumps(REG_CT_DICT, indent=2)

register = template.Library()

class InsertModels(template.Node):
    def render(self, context):
        return REG_CT_JSON

@register.tag
def insert_admin_apps(parser, token):
    return InsertModels()

class TagSuggesterUrl(template.Node):
    def render(self, context):
        from django.core.urlresolvers import reverse
        return reverse('tag_suggester')

@register.tag
def tag_suggester_url(parser, token):
    return TagSuggesterUrl()

