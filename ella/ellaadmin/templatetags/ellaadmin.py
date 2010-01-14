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
        tag_name, o_id = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, \
            '"%s" tag requires exactly two arguments - content_type_id and object_id.' % token.contents.split()[0]
    return FormatHitsLink(o_id)


class TagSuggesterUrl(template.Node):
    def render(self, context):
        from django.core.urlresolvers import reverse
        return reverse('tag_suggester')

@register.tag
def tag_suggester_url(parser, token):
    return TagSuggesterUrl()


class FormatHitsLink(template.Node):
    def __init__(self, target_id):
        self.target_id = target_id

    def render(self, context):
        from django.utils.safestring import mark_safe
        from ella.core.cache import get_cached_list
        from ella.core.models import HitCount, Placement
        try:
            oid = template.Variable(self.target_id).resolve(context)
            # TODO: this improve speed but it's dirty
            #if not tct in [16,28,29,55,32]:
            #    return ''
            hl = get_cached_list(
                    Placement,
                    publishable=oid
            )
            l = ''
            for h in hl:
                hit_count = HitCount.objects.get(placement=h)
                if not hit_count:
                    continue
                l += '<li><a href="../../../core/hitcount/%d/" class="viewsitelink">Hits: %d</a></li>' \
                % (hit_count._get_pk_val(), hit_count.hits)
            # return mark_safe(l)
            return mark_safe(u'<!--  here is hidden hitcount button:  %s -->' % l )
        except (HitCount.DoesNotExist, template.VariableDoesNotExist):
            return ''
