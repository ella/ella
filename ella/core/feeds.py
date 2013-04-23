from mimetypes import guess_type

from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from django.http import Http404
from django.template import TemplateDoesNotExist, RequestContext, NodeList

from ella.core.models import Listing, Category
from ella.core.conf import core_settings
from ella.core.managers import ListingHandler
from ella.photos.models import Format, FormatedPhoto


class RSSTopCategoryListings(Feed):
    format_name = None

    def __init__(self, *args, **kwargs):
        super(RSSTopCategoryListings, self).__init__(*args, **kwargs)

        if core_settings.RSS_ENCLOSURE_PHOTO_FORMAT:
            self.format_name = core_settings.RSS_ENCLOSURE_PHOTO_FORMAT

        if self.format_name is not None:
            self.format = Format.objects.get_for_name(self.format_name)
        else:
            self.format = None

    def get_object(self, request, category=''):
        bits = category.split('/')
        try:
            cat = Category.objects.get_by_tree_path(u'/'.join(bits))
        except Category.DoesNotExist:
            raise Http404()

        self.box_context = RequestContext(request)

        return cat

    def items(self, obj):
        qset = Listing.objects.get_queryset_wrapper(category=obj, children=ListingHandler.ALL)
        return qset.get_listings(count=core_settings.RSS_NUM_IN_FEED)

    # Feed metadata
    ###########################################################################
    def title(self, obj):
        return obj.app_data.get('syndication', {}).get('title', obj.title)

    def link(self, obj):
        return obj.get_absolute_url()

    def description(self, obj):
        return obj.app_data.get('syndication', {}).get('description', obj.description)

    # Item metadata
    ###########################################################################
    def item_guid(self, item):
        return str(item.publishable.pk)

    def item_pubdate(self, item):
        return item.publish_from

    def item_title(self, item):
        return item.publishable.title

    def item_link(self, item):
        return item.get_absolute_url()

    def item_description(self, item):
        if not core_settings.RSS_DESCRIPTION_BOX_TYPE:
            return item.publishable.description

        p = item.publishable
        box = p.box_class(p, core_settings.RSS_DESCRIPTION_BOX_TYPE, NodeList())
        try:
            desc = box.render(self.box_context)
        except TemplateDoesNotExist:
            desc = None

        if not desc:
            desc = item.publishable.description
        return desc

    def item_author_name(self, item):
        return ', '.join(map(unicode, item.publishable.authors.all()))

    # Enclosure - Photo
    ###########################################################################
    def item_enclosure_url(self, item):
        if not hasattr(item, '__enclosure_url'):
            if hasattr(item.publishable, 'feed_enclosure'):
                item.__enclosure_url = item.publishable.feed_enclosure()['url']
            elif self.format is not None and item.publishable.photo_id:
                item.__enclosure_url = FormatedPhoto.objects.get_photo_in_format(item.publishable.photo_id, self.format)['url']
            else:
                item.__enclosure_url = None

        return item.__enclosure_url

    def item_enclosure_mime_type(self, item):
        enc_url = self.item_enclosure_url(item)
        if enc_url:
            return guess_type(enc_url)[0]

    def item_enclosure_length(self, item):
        # make sure get_photo_in_format was called
        if hasattr(item.publishable, 'feed_enclosure'):
            return item.publishable.feed_enclosure()['size']
        elif self.format:
            fp, created = FormatedPhoto.objects.get_or_create(photo=item.publishable.photo_id, format=self.format)
            return fp.image.size

class AtomTopCategoryListings(RSSTopCategoryListings):
    feed_type = Atom1Feed
    subtitle = RSSTopCategoryListings.description

