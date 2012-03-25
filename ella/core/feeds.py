from mimetypes import guess_type

from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from django.http import Http404
from django.template import TemplateDoesNotExist, RequestContext, NodeList

from ella.core.models import Listing, Category
from ella.core.conf import core_settings
from ella.core.managers import ListingHandler
from ella.core.box import Box
from ella.photos.models import Format, FormatedPhoto

class RSSTopCategoryListings(Feed):
    def __init__(self, *args, **kwargs):
        super(RSSTopCategoryListings, self).__init__(*args, **kwargs)
        if core_settings.RSS_ENCLOSURE_PHOTO_FORMAT:
            self.format = Format.objects.get_for_name(core_settings.RSS_ENCLOSURE_PHOTO_FORMAT)
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
        kwa = {}
        kwa['category'] = obj

        # TODO: In ella based application children attr can be NONE, IMMEDIATE and ALL
        if kwa['category'].tree_parent != None:
            kwa['children'] = ListingHandler.ALL

        qset = Listing.objects.get_queryset_wrapper(**kwa)
        return qset.get_listings(count=core_settings.RSS_NUM_IN_FEED)

    # Feed metadata
    ###########################################################################
    def title(self, obj):
        return obj.app_data.get('syndication', {}).get('title', obj.title)

    def link(self, obj):
        return obj.get_absolute_url()

    def description(self, obj):
        return obj.app_data.get('syndication', {}).get('title', obj.description)

    # Item metadata
    ###########################################################################
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
            return box.render(self.box_context)
        except TemplateDoesNotExist:
            return item.publishable.description

    # Enclosure - Photo
    ###########################################################################
    def item_enclosure_url(self, item):
        if not hasattr(item, '__enclosure_url'):
            if item.publishable.photo_id:
                if self.format:
                    item.__enclosure_url = FormatedPhoto.objects.get_photo_in_format(item.publishable.photo_id, self.format)['url']
                else:
                    item.__enclosure_url = item.publishable.photo.image.url
            else:
                item.__enclosure_url = None

        return item.__enclosure_url

    def item_enclosure_mime_type(self, item):
        im = self.item_enclosure_url(item)
        if im:
            return guess_type(im)[0]

    def item_enclosure_size(self, item):
        # make sure get_photo_in_format was called
        if self.item_enclosure_url(item):
            if self.format:
                return FormatedPhoto.objects.get(photo=item.publishable.photo_id, format=self.format).image.size
            else:
                return item.publishable.photo.image.size

class AtomTopCategoryListings(RSSTopCategoryListings):
    feed_type = Atom1Feed
    subtitle = RSSTopCategoryListings.description

