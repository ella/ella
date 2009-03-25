from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import Http404
from django.utils.translation import ungettext

from ella.core.views import get_templates_from_placement


def gallery_item_detail(request, context, item_slug=None):
    '''get GalleryItem object by its slug or first one (given by GalleryItem.order) from gallery'''

    gallery = context['object']
    item_sorted_dict = gallery.items
    count = len(item_sorted_dict)
    count_str = ungettext('%(count)d object total', '%(count)d objects total', count)  % {'count': count}
    next = None
    previous = None

    if count == 0:
        raise Http404()
        # TODO: log empty gallery

    if item_slug is None:
        item, target = item_sorted_dict.value_for_index(0)
        if count > 1:
            next = item_sorted_dict.value_for_index(1)[0]
        position = 1
    else:
        try:
            item, target = item_sorted_dict[item_slug]
        except KeyError, e:
            raise Http404()
        item_index = item_sorted_dict.keyOrder.index(item_slug)
        if item_index > 0:
            previous = item_sorted_dict.value_for_index(item_index-1)[0]
        if (item_index+1) < count:
            next = item_sorted_dict.value_for_index(item_index+1)[0]
        position = item_index + 1

    context['object'] = target

    context.update({
            'gallery': gallery,
            'item': item,
            'object' : target,
            'item_list' : item_sorted_dict.values(),
            'next' : next,
            'previous' : previous,
            'count' : count,
            'count_str' : count_str,
            'position' : position,
    })

    return render_to_response(
        get_templates_from_placement('item.html', context['placement']),
        context,
        context_instance=RequestContext(request),
    )

def items(request, bits, context):
    " Wrapper around gallery_item_detail. "
    if len(bits) != 1:
        raise Http404()

    return gallery_item_detail(request, context, bits[0])


