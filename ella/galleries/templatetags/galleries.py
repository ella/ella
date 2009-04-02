import math

from django import template
from django.utils import simplejson

register = template.Library()

def gallery_func(func, value, param):
    if not ',' in param:
        raise template.TemplateSyntaxError, "gallery filters take one parameter in format COUNT_PER_PAGE,PAGE_WIDTH"
    on_page, per_page = param.split(',')
    try:
        value = int(value)
        on_page, per_page = int(on_page), int(per_page)
    except ValueError:
        raise template.TemplateSyntaxError, "Value and parameters to gallery filters must be integers"

    return func(value, on_page, per_page)

@register.filter
def gallery_offset(value, param):
    " Helper template filter to calculate position of the preview pane. "
    return gallery_func(lambda x,y,z: (math.floor((x-1) / float(y))) * z, value, param)

@register.filter
def gallery_width(value, param):
    " Helper template filter to calculate width of the preview pane. "
    return gallery_func(lambda x,y,z: (math.ceil(x / float(y))) * z, value, param)

@register.simple_tag
def gallery_content_json(gallery, thumb_format):
    """
    Returns gallery items as a JSON object
    Ussage:
    gallery_content_json gallery "photo_format_name"
    """

    photos = []

    for item_key in gallery.items:
        gallery_item, target_object = gallery.items[item_key]
        photos.append({
                       'src': target_object.get_formated_photo(thumb_format).url,
                       'link': gallery_item.get_absolute_url(),
                       'ajaxLink': gallery_item.get_absolute_url(),
                       'alt': target_object.description
                      })

    content = { 'thumbnails': photos }

    return simplejson.dumps( photos, ensure_ascii=False, indent=4 )
