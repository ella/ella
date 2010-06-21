from django import template
from ella.newman.utils import get_newman_url
from ella.core.models.publishable import HitCount
from ella.positions.models import Position

register = template.Library()

@register.inclusion_tag('newman/tpl_tags/newman_frontend_admin.html', takes_context=True)
def newman_frontend_admin(context):
    user = context['user']
    vars = {}

    if not user.is_staff:
        return vars

    #vars['logout_url'] = reverse('newman:logout')
    object = context.get('object')
    if 'gallery' in context:
        object = context.get('gallery')
    placement = context.get('placement')

    vars['user'] = user
    vars['STATIC_URL'] = context.get('STATIC_URL')
    vars['NEWMAN_MEDIA_URL'] = context.get('NEWMAN_MEDIA_URL')
    vars['placement'] = placement
    vars['category'] = context.get('category')
    vars['newman_index_url'] = 'http://localhost:3001/'

    from django.db.models import Q
    import datetime
    now = datetime.datetime.now()
    lookup = (Q(active_from__isnull=True) | Q(active_from__lte=now)) & (Q(active_till__isnull=True) | Q(active_till__gt=now))
    positions = Position.objects.filter(lookup, category=vars['category'].pk, disabled=False, target_id__isnull=False)
    #print positions.query
    vars['positions'] = positions

    if object:
        vars['object'] = object
        vars['newman_object_url'] = get_newman_url(object)
        vars['hitcount'] = HitCount.objects.get(placement=placement.pk)

    return vars
