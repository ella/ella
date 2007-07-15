from django.conf.urls.defaults import *

from ella.core.views import object_detail, list_content_type, category_detail, home

# list of objects in category
urlpatterns = patterns('',
    url(r'^(?P<category>[-\w/]+)/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<content_type>[\w-]+)/(?P<slug>[\w-]+)/$',
        object_detail, name="object_detail"),
    url(r'^(?P<category>[-\w/]+)/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<content_type>[\w-]+)/$',
        list_content_type, name="category_list_content_type_day"),
    url(r'^(?P<category>[-\w/]+)/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<content_type>[\w-]+)/$',
        list_content_type, name="category_list_content_type_month"),
    url(r'^(?P<category>[-\w/]+)/(?P<year>\d{4})/(?P<content_type>[\w-]+)/$',
        list_content_type, name="category_list_content_type_year"),
    url(r'^(?P<category>[-\w/]+)/(?P<content_type>[\w-]+)/$', list_content_type, name="category_list_content_type",),

    # category homepage
    url(r'^(?P<category>[-\w]+)/$', category_detail, name="category_detail"),
)

# list of objects regardless of category
urlpatterns += patterns('',
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<content_type>[\w-]+)/$',
        list_content_type, name="list_content_type_day"),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<content_type>[\w-]+)/$', list_content_type, name="list_content_type_month"),
    url(r'^(?P<year>\d{4})/(?P<content_type>[\w-]+)/$', list_content_type, name="list_content_type_year"),
)

urlpatterns += patterns('',
    url(r'^$', home, name="root_homepage"),
)
