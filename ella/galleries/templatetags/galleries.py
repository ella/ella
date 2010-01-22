import math
import anyjson

from django import template
from django.template.defaultfilters import striptags

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
    gallery_content_json <gallery> "photo_format_name"
    """

    photos = []

    for item_key in gallery.items:
        gallery_item, target_object = gallery.items[item_key]
        formated_photo = target_object.get_formated_photo(thumb_format)
        if formated_photo is not None:
            photos.append({
                           'src': formated_photo.url,
                           'link': gallery_item.get_absolute_url(),
                           'ajaxLink': gallery_item.get_absolute_url(),
                           'alt': striptags(target_object.description)
                          })

    return anyjson.serialize(photos)

@register.tag
def gallery_navigation(parser, token):
    """
    Template tag gallery_navigation

    Usage::
        {% gallery_navigation for <gallery> step <X> current_position <X> as <result> %}

    Example::
        {% gallery_navigation for gallery step 5 current_position 8 as navigation %}
    """

    try:
        tag_name, for_arg, gallery, step_arg, step, position_arg, position, as_arg, result = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "Four arguments are expected in %r tag" % token.split_contents()[0]

    params = {}

    if for_arg == 'for':
        params['for'] = gallery
    else:
        raise template.TemplateSyntaxError, "Unknown argument %r in tag %r" % (for_arg, tag_name)
    if step_arg == 'step':
        params['step'] = step
    else:
        raise template.TemplateSyntaxError, "Unknown argument %r in tag %r" % (step_arg, tag_name)
    if position_arg == 'current_position':
        params['position'] = position
    else:
        raise template.TemplateSyntaxError, "Unknown argument %r in tag %r" % (position_arg, tag_name)
    if as_arg == 'as':
        params['as'] = result
    else:
        raise template.TemplateSyntaxError, "Unknown argument %r in tag %r" % (as_arg, tag_name)

    return GalleryNavigationNode(params)

class GalleryNavigationNode(template.Node):
    def __init__(self, params):
        self.params = params

    def render(self, context):
        gallery = template.Variable( self.params['for'] ).resolve(context)
        position = template.Variable( self.params['position'] ).resolve(context)
        step = int( self.params['step'] )

        count = len( gallery.items )
        navigation = []

        if count > 0:
            keys = gallery.items.keys()

            # Last page number
            last_page = count / step
            if last_page * step < count:
                 last_page = last_page + 1
            # Current page number
            current_position_page = position / step
            if current_position_page * step < position:
                current_position_page = current_position_page + 1
            # Previous and next page url (first item on page url)
            previous_page = current_position_page - 1
            previous_page_url = previous_page > 0 and gallery.items[ keys[previous_page * step - step] ][0].get_absolute_url() or None
            next_page = current_position_page
            next_page_url = next_page < last_page and gallery.items[ keys[next_page * step] ][0].get_absolute_url() or None

            for i in range(0, last_page):
                page = i + 1
                # First and last item on page number
                start_item = i * step + 1
                stop_item  = i * step + step
                if stop_item > count:
                    stop_item = count
                # Is it current page?
                on_current_page = current_position_page == page and True or False

                navigation.append({
                                   'first_item_url': gallery.items[ keys[i * step] ][0].get_absolute_url(),
                                   'start_item_number': start_item,
                                   'stop_item_number': stop_item,
                                   'page_number': page,
                                   'on_current_page': on_current_page
                                  })
        else:
            current_position_page = None
            previous_page_url = None
            next_page_url = None

        context[ self.params['as'] ] = {
                                        'current_page_number': current_position_page,
                                        'previous_page_url': previous_page_url,
                                        'next_page_url': next_page_url,
                                        'pages': navigation
                                       }
        return ''
