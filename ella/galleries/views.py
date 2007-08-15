from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.http import Http404

from ella.core.custom_urls import dispatcher

from ella.galleries.models import Gallery, GalleryItem


def gallery_item_detail(request, gallery, item_slug=None):
    '''get GalleryItem object by its slug or first one (given by GalleryItem.order) from gallery'''
    context = {
        'gallery': gallery,
        'gallery_item': gallery_item,
}
    return render_to_response('galleries/item_detail.html', context)

def items(request, bits, context):
    if len(bits) == 0:
        return gallery_item_detail(request, context['object'])
    if len(bits) == 1:
        slug = bits[0]
        return gallery_item_detail(request, context['object'], slug)

    raise Http404


def register_custom_urls():
    """register all custom urls"""
    dispatcher.register(slugify(_('items')), items)


