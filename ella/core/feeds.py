from django.contrib.syndication.feeds import Feed
from django.contrib.contenttypes.models import ContentType
from django.utils.feedgenerator import Atom1Feed
from django.utils.translation import ugettext_lazy as _
from django.http import Http404
from django.conf import settings

from ella.core.models import Listing, Category
from ella.core.views import get_content_type
from ella.core.cache.utils import get_cached_object, get_cached_object_or_404
from ella.core.conf import core_settings


class RSSTopCategoryListings(Feed):
    def get_object(self, bits):
        try:
            ct = get_content_type(bits[-1])
            bits = bits[:-1]
        except (Http404, IndexError):
            ct = False

        if bits:
            cat = get_cached_object_or_404(Category, tree_path=u'/'.join(bits), site__id=settings.SITE_ID)
        else:
            cat = get_cached_object(Category, tree_parent__isnull=True, site__id=settings.SITE_ID)

        if ct:
            return (cat, ct)
        return cat

    def title(self, obj):
        if isinstance(obj, tuple):
            category, content_type = obj
            return _('Top %(count)d %(ctype)s objects in category %(cat)s.') % {
                    'count' : core_settings.RSS_NUM_IN_FEED,
                    'ctype' : content_type.model_class()._meta.verbose_name_plural,
                    'cat' : category.title
            }
        elif obj:
            return _('Top %(count)d objects in category %(cat)s.') % {
                    'count' : core_settings.RSS_NUM_IN_FEED,
                    'cat' : obj.title
            }
        else:
            obj = get_cached_object(Category, tree_parent__isnull=True, site__id=settings.SITE_ID)
            return _('Top %(count)d objects in category %(cat)s.') % {
                    'count' : core_settings.RSS_NUM_IN_FEED,
                    'cat' : obj.title
            }

    def items(self, obj):
        kwa = {}
        if isinstance(obj, tuple):
            category, content_type = obj
            kwa['content_types'] = [ content_type ]
            kwa['category'] = category
        elif obj:
            kwa['category'] = obj
        else:
            kwa['category'] = get_cached_object(Category, tree_parent__isnull=True, site__id=settings.SITE_ID)

        # TODO: In ella based application children attr can be NONE, IMMEDIATE and ALL
        if kwa['category'].tree_parent != None:
            kwa['children'] = Listing.objects.ALL

        return Listing.objects.get_listing(count=core_settings.RSS_NUM_IN_FEED, **kwa)

    def link(self, obj):
        if isinstance(obj, tuple):
            return obj[0].get_absolute_url()
        elif obj:
            return obj.get_absolute_url()
        else:
            return '/'

    def description(self, obj):
        return self.title(obj)

    def item_pubdate(self, item):
        return item.publish_from

    def item_enclosure_url(self, item):
        if getattr(item.target, 'photo'):
            return item.target.photo.image.url

    def item_enclosure_length(self, item):
        if getattr(item.target, 'photo'):
            return item.target.photo.image.size

    def item_enclosure_mime_type(self, item):
        if getattr(item.target, 'photo'):
            if item.target.photo.image.name.endswith('.jpg'):
                return 'image/jpeg'
            elif item.target.photo.image.name.endswith('.png'):
                return 'image/png'
            return 'image/gif'

class AtomTopCategoryListings(RSSTopCategoryListings):
    feed_type = Atom1Feed
    subtitle = RSSTopCategoryListings.description

