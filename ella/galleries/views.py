from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext
from django.template.defaultfilters import slugify
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import Http404

from ella.core.custom_urls import dispatcher
from ella.core.cache.utils import get_cached_object
from ella.core.models import Category

from ella.galleries.models import Gallery


def gallery_item_detail(request, gallery, item_slug=None):
    '''get GalleryItem object by its slug or first one (given by GalleryItem.order) from gallery'''

    item_list = gallery.items
    count = len(item_list)

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


    category = get_cached_object(Category, pk=gallery.category_id)
    return render_to_response(
                [
                    'page/category/%s/galleries/%s/item.html' % (category.path, gallery.slug,)
                    'page/category/%s/galleries/item.html' % (category.path,),
                    'page/galleries/item.html',
                ],
                {
                    'gallery': gallery,
                    'item': item,
                    'object' : target,
                    'item_list' : item_list,
                    'next' : next,
                    'previous' : previous,
                    'count' : count,
                    'position' : position,
},
                context_instance=RequestContext(request),
)

def items(request, bits, context):
    if len(bits) == 0:
        return gallery_item_detail(request, context['object'])

    if len(bits) == 1:
        slug = bits[0]
        return gallery_item_detail(request, context['object'], slug)

    raise Http404


def register_custom_urls():
    """register all custom urls"""
    dispatcher.register(slugify(ugettext('items')), items, model=Gallery)


