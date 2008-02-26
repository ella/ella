from django.template.defaultfilters import slugify
from django.utils.translation import ugettext

from ella.galleries.views import gallery_item_detail, items
from ella.galleries.models import Gallery
from ella.core.custom_urls import dispatcher

dispatcher.register_custom_detail(Gallery, gallery_item_detail)
dispatcher.register(slugify(ugettext('items')), items, model=Gallery)

