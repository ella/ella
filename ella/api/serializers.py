from ella.api import object_serializer, response_serializer, FULL
from ella.api.conf import api_settings
from ella.core.models import Category, Publishable, Listing, Author
from ella.photos.models import FormatedPhoto, Photo

from django.core.paginator import Page
from django.utils import simplejson

def serialize_list(request, l):
    return [object_serializer.serialize(request, o) for o in l]

def serialize_dict(request, d):
    return dict((k, object_serializer.serialize(request, v)) for k, v in d.iteritems())

def serialize_page(request, page):
    return {
        'total': page.paginator.count,
        'per_page': page.paginator.per_page,
        'num_pages': page.paginator.num_pages,
        'current_page': page.number,
        'objects': serialize_list(request, page.object_list),
    }

def serialize_full_category(request, category):
    page_no = 1
    if 'p' in request.GET and request.GET['p'].isdigit():
        page_no = int(request.GET['p'])
    return object_serializer.serialize(request, {'category': category, 'listings': category.app_data.ella.get_listings_page(page_no)})

def serialize_category(request, category):
    return {
        'id': category.pk,
        'title': category.title,
        'tree_path': category.tree_path,
    }

def serialize_author(request, author):
    return {
        'name': author.name,
        'url': author.get_absolute_url(),
    }

def serialize_photo(request, photo, formats=None):
    if formats is None:
        formats = api_settings.DEFAULT_PHOTO_FORMATS
    return dict((f, FormatedPhoto.objects.get_photo_in_format(photo, f, False)) for f in formats)

def serialize_publishable(request, publishable):
    return {
        'id': publishable.id,
        'url': publishable.get_absolute_url(),
        'content_type': publishable.content_type.name,
        'description': publishable.description,
        # don't use object_serializer to avoid fetching Photo model instance
        'photo': serialize_photo(request, publishable.photo_id, formats=api_settings.PUBLISHABLE_PHOTO_FORMATS),
    }

def serialize_listing(request, listing):
    return object_serializer.serialize(request, listing.publishable)

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

