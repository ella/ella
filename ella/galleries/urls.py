from django.template.defaultfilters import slugify
from django.utils.translation import ugettext
from django.conf.urls.defaults import patterns, url

from ella.galleries.views import gallery_item_detail
from ella.galleries.models import Gallery
from ella.core.custom_urls import resolver


urlpatterns = patterns('',
    url(r'^(?P<item_slug>[\w-]+)/$', gallery_item_detail, name='gallery-item-detail'),
)

resolver.register(urlpatterns, prefix=slugify(ugettext('Item')), model=Gallery)
resolver.register_custom_detail(Gallery, gallery_item_detail)
