from ella.api import object_serializer, response_serializer, PARTIAL, FULL
from ella.api.conf import api_settings
from ella.core.models import Category, Publishable, Listing, Author
from ella.photos.models import FormatedPhoto, Photo

from django.core.paginator import Page
from django.utils import simplejson
from django.conf import settings

def serialize_list(l):
    return [object_serializer.serialize(o, 'list') for o in l]

def serialize_dict(d):
    return dict((k, object_serializer.serialize(v)) for k, v in d.iteritems())

def serialize_page(page):
    return {
        'total': page.paginator.count,
        'per_page': page.paginator.per_page,
        'num_pages': page.paginator.num_pages,
        'current_page': page.number,
        'objects': serialize_list(page.object_list),
    }

def serialize_full_category(category):
    # FIXME: need to pass in request so we can access page param
    return {'category': serialize_category(category), 'listings': serialize_page(category.app_data.ella.get_listings_page(1))}

def serialize_category(category):
    return {
        'id': category.pk,
        'title': category.title,
        'tree_path': category.tree_path,
    }

def serialize_author(author):
    return {
        'name': author.name,
        'url': author.get_absolute_url(),
    }

def serialize_photo(photo, formats=None):
    if formats is None:
        formats = api_settings.DEFAULT_PHOTO_FORMATS
    out = dict((f, FormatedPhoto.objects.get_photo_in_format(photo, f, False)) for f in formats)
    for fp in out.itervalues():
        fp['url'] = settings.MEDIA_URL + fp['url']
    return out

def serialize_publishable(publishable):
    return {
        'id': publishable.id,
        'url': publishable.get_absolute_url(),
        'content_type': publishable.content_type.name,
        'description': publishable.description,
        # don't use object_serializer to avoid fetching Photo model instance
        'photo': serialize_photo(publishable.photo_id, formats=api_settings.PUBLISHABLE_PHOTO_FORMATS),
    }

def serialize_listing(listing):
    return object_serializer.serialize(listing.publishable, PARTIAL)

response_serializer.register('application/json', simplejson.dumps)

object_serializer.register(list, serialize_list)
object_serializer.register(dict, serialize_dict)
object_serializer.register(tuple, serialize_list)
object_serializer.register(Page, serialize_page)
object_serializer.register(Author, serialize_author)
object_serializer.register(Category, serialize_category)
object_serializer.register(Category, serialize_full_category, FULL)
object_serializer.register(Photo, serialize_photo)
object_serializer.register(Publishable, serialize_publishable)
object_serializer.register(Listing, serialize_listing)

