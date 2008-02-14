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

@register.tag
def get_hits_link(parser, token):
    try:
        tag_name, ct_id, o_id = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, \
            '"%s" tag requires exactly two arguments - content_type_id and object_id.' % token.contents.split()[0]
    return FormatHitsLink(ct_id, o_id)

class FormatHitsLink(template.Node):

    def __init__(self, target_ct, target_id):
        self.target_ct = target_ct
        self.target_id = target_id

    def render(self, context):
        from django.utils.safestring import mark_safe
        from ella.core.cache import get_cached_list
        from ella.core.models import HitCount
        from django.template import resolve_variable
        try:
            tct = resolve_variable(self.target_ct, context)
            oid = resolve_variable(self.target_id, context)
            # TODO: this improve speed but it's dirty
            if not tct in [16,28,29,55,32]:
                return ''
            hl = get_cached_list(
                    HitCount,
                    target_ct=tct,
                    target_id=oid
)
            l = ''
            for h in hl:
                l += '<li><a href="../../../core/hitcount/%d/" class="viewsitelink">Hits (%s): %d</a></li>' % (h.id, h.site.name, h.hits)
            return mark_safe(l)
        except (HitCount.DoesNotExist, template.VariableDoesNotExist):
            return ''
