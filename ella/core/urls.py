from django.conf.urls.defaults import *

from ella.core.views import object_detail, list_content_type, category_detail, home
from ella.core.feeds import RSSTopCategoryListings, AtomTopCategoryListings

feeds = {
    'rss' : RSSTopCategoryListings,
    'atom' : AtomTopCategoryListings,
}

# list of objects in category
urlpatterns = patterns('',
    # home page
    url(r'^$', home, name="root_homepage"),

    # rsss feeds
    url(r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}, name="feeds"),

    # list of objects regadless of category and content type
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$',
        list_content_type, name="list_day"),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$', list_content_type, name="list_month"),
    url(r'^(?P<year>\d{4})/$', list_content_type, name="list_year"),

    # list of objects regardless of category
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<content_type>[\w-]+)/$',
        list_content_type, name="list_content_type_day"),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<content_type>[\w-]+)/$', list_content_type, name="list_content_type_month"),
    url(r'^(?P<year>\d{4})/(?P<content_type>[\w-]+)/$', list_content_type, name="list_content_type_year"),

    # object detail
    url(r'^(?P<category>[-\w/]+)/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<content_type>[\w-]+)/(?P<slug>[\w-]+)/$',
        object_detail, name="object_detail"),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<content_type>[\w-]+)/(?P<slug>[\w-]+)/$',
        object_detail, {'category' : ''}, name="home_object_detail"),

    # category listings
    url(r'^(?P<category>[-\w/]+)/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<content_type>[\w-]+)/$',
        list_content_type, name="category_list_content_type_day"),
    url(r'^(?P<category>[-\w/]+)/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<content_type>[\w-]+)/$',
        list_content_type, name="category_list_content_type_month"),
    url(r'^(?P<category>[-\w/]+)/(?P<year>\d{4})/(?P<content_type>[\w-]+)/$',
        list_content_type, name="category_list_content_type_year"),

    # category homepage
    url(r'^(?P<category>[-\w/]+)/$', category_detail, name="category_detail"),

)
