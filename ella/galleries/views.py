from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext
from django.template.defaultfilters import slugify
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import Http404

from ella.core.custom_urls import dispatcher

from ella.galleries.models import Gallery


def gallery_item_detail(request, context, item_slug=None):
    '''get GalleryItem object by its slug or first one (given by GalleryItem.order) from gallery'''

    gallery = context['object']
    category = context['category']
    item_list = gallery.items
    count = len(item_list)

    if count == 0:
        raise Http404
        # TODO: log empty gallery

    if item_slug is None:
        previous = None
        item, target = item_list[0]
        if count > 1:
            next = item_list[1][0]
        else:
            next = None
        position = 1
        item_slug = item.get_slug(item_list)
    else:
        for i, (it, obj) in enumerate(item_list):
            if it.get_slug(item_list) == item_slug:
                item, target = it, obj
                if i > 0:
                    previous = item_list[i-1][0]
                else:
                    previous = None

                if (i+1) < count:
                    next = item_list[i+1][0]
                else:
                    next = None

                position = i + 1
                break
        else:
            raise Http404

    context['object'] = target

    context.update({
            'gallery': gallery,
            'item': item,
            'object' : target,
            'item_list' : item_list,
            'next' : next,
            'previous' : previous,
            'count' : count,
            'position' : position,
})

    return render_to_response(
                [
                    'page/category/%s/content_type/galleries.gallery/%s/item.html' % (category.path, gallery.slug,),
                    'page/category/%s/content_type/galleries.gallery/item.html' % (category.path,),
                    'page/content_type/galleries.gallery/item.html',
                ],
                context,
                context_instance=RequestContext(request),
)

def items(request, bits, context):
    if len(bits) != 1:
        raise Http404

    return gallery_item_detail(request, context, bits[0])

def register_custom_urls():
    """register all custom urls"""
    dispatcher.register_custom_detail(Gallery, gallery_item_detail)
    dispatcher.register(slugify(ugettext('items')), items, model=Gallery)


