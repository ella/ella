from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from django.utils.translation import ugettext_lazy as _
from django.http import Http404
from django.conf import settings

from ella.core.models import Listing, Category
from ella.core.views import get_content_type
from ella.core.cache.utils import get_cached_object
from ella.core.conf import core_settings
from ella.core.managers import ListingHandler
from ella.photos.models import Format

class RSSTopCategoryListings(Feed):
    def get_object(self, request, category=''):
        bits = category.split('/')
        try:
            ct = get_content_type(bits[-1])
            bits = bits[:-1]
        except (Http404, IndexError):
            ct = False

        if bits:
            try:
                cat = Category.objects.get_by_tree_path(u'/'.join(bits))
            except Category.DoesNotExist:
                raise Http404()
        else:
            cat = Category.objects.get_by_tree_path('')

        if ct:
            return (cat, ct)
        return cat

    def title(self, obj):
        def syndication_title(category):
            if 'syndication' in category.app_data and 'title' in category.app_data['syndication']:
                return category.app_data['syndication']['title']
            return category.title

        if isinstance(obj, tuple):
            category, content_type = obj
            return _('%(ctype)s from %(cat)s.') % {
                    'ctype' : content_type.model_class()._meta.verbose_name_plural,
                    'cat' : syndication_title(category)
            }
        elif obj:
            return syndication_title(obj)
        else:
            obj = Category.objects.get_by_tree_path('')
            return syndication_title(obj)

    def items(self, obj):
        kwa = {}
        if isinstance(obj, tuple):
            category, content_type = obj
            kwa['content_types'] = [ content_type ]
            kwa['category'] = category
        elif obj:
            kwa['category'] = obj
        else:
            kwa['category'] = Category.objects.get_by_tree_path('')

        # TODO: In ella based application children attr can be NONE, IMMEDIATE and ALL
        if kwa['category'].tree_parent != None:
            kwa['children'] = ListingHandler.ALL

        return Listing.objects.get_listing(count=core_settings.RSS_NUM_IN_FEED, **kwa)

    def link(self, obj):
        if isinstance(obj, tuple):
            return obj[0].get_absolute_url()
        elif obj:
            return obj.get_absolute_url()
        else:
            return '/'

    def description(self, obj):
        if 'syndication' in obj.app_data and 'description' in obj.app_data['syndication']:
            return obj.app_data['syndication']['description']
        return self.title(obj)

    def item_pubdate(self, item):
        return item.publish_from

    def get_enclosure_image(self, item, enc_format=core_settings.RSS_ENCLOSURE_PHOTO_FORMAT):
        if getattr(item.publishable, 'photo'):
            if enc_format is not None:
                try:
                    return item.publishable.photo.get_formated_photo(enc_format)
                except Format.DoesNotExist:
                    pass
            return item.publishable.photo.get_image_info()

    def get_enclosure_image_attr(self, item, attr):
        image = self.get_enclosure_image(item)
        if image is not None:
            return image.get(attr, None)
        return None

    def item_enclosure_url(self, item):
        return self.get_enclosure_image_attr(item, 'url')

    def item_enclosure_length(self, item):
        try:
            return self.get_enclosure_image_attr(item, 'size')
        except OSError:
            pass

    def item_enclosure_mime_type(self, item):
        image = self.get_enclosure_image(item)
        if image is not None:
            if image['url'].endswith('.jpg'):
                return 'image/jpeg'
            elif image['url'].endswith('.png'):
                return 'image/png'
            return 'image/gif'

class AtomTopCategoryListings(RSSTopCategoryListings):
    feed_type = Atom1Feed
    subtitle = RSSTopCategoryListings.description

