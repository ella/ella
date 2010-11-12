from django import template
from django.contrib.contenttypes.models import ContentType

from ella.newman.conf import newman_settings
from ella.ellacomments.newman_admin import MODELS_WITH_COMMENTS
from ella.core.models.publishable import HitCount
from ella.positions.models import Position

register = template.Library()

def get_newman_url(obj):
    """ Assembles edit-object url for Newman admin. """
    ct = ContentType.objects.get_for_model(obj)
    url = '%(base)s#/%(app)s/%(model)s/%(pk)d/' % {
        'base': newman_settings.BASE_URL,
        'app': ct.app_label,
        'model': ct.model,
        'pk': obj.pk
    }
    return url

def get_moderation_url(obj):
    ct = ContentType.objects.get_for_model(obj)
    model_id = '%s.%s' % (ct.app_label, ct.model)
    if model_id in MODELS_WITH_COMMENTS:
        return '%(base)s#/threadedcomments/threadedcomment/?content_type=%(ct_id)d&object_pk=%(obj_pk)s' % {
            'base': newman_settings.BASE_URL,
            'ct_id': ct.id,
            'obj_pk': obj._get_pk_val(),
        }

@register.inclusion_tag('newman/tpl_tags/newman_frontend_admin.html', takes_context=True)
def newman_frontend_admin(context):
    user = context['user']
    vars = {}

    if not user or not user.is_staff:
        return vars

    #vars['logout_url'] = reverse('newman:logout')
    obj = context.get('object')
    if 'gallery' in context:
        obj = context.get('gallery')
    placement = context.get('placement')

    vars['user'] = user
    vars['STATIC_URL'] = context.get('STATIC_URL')
    vars['NEWMAN_MEDIA_URL'] = context.get('NEWMAN_MEDIA_URL')
    vars['placement'] = placement
    vars['category'] = context.get('category')
    vars['newman_index_url'] = newman_settings.BASE_URL
    category = vars['category']
    if not category or not category.pk:
        return vars

    from django.db.models import Q
    import datetime
    now = datetime.datetime.now()
    lookup = (Q(active_from__isnull=True) | Q(active_from__lte=now)) & (Q(active_till__isnull=True) | Q(active_till__gt=now))
    positions = Position.objects.filter(lookup, category=category.pk, disabled=False, target_id__isnull=False)
    #print positions.query
    vars['positions'] = positions

    if obj:
        vars['object'] = obj
        vars['newman_object_url'] = get_newman_url(obj)
        vars['newman_comment_moderation_url'] = get_moderation_url(obj)
        if placement:
            vars['hitcount'] = HitCount.objects.get(placement=placement.pk)

    return vars


logout_url = newman_settings.BASE_URL + 'logout/'
class NewmanLogoutNode(template.Node):
    def render(self, context):
        return logout_url

@register.tag
def newman_frontend_logout(parser, token):
    return NewmanLogoutNode()
