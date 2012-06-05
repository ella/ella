from django.conf.urls.defaults import patterns, url
from django.core.validators import slug_re
from django.conf import settings

from ella.core.feeds import RSSTopCategoryListings, AtomTopCategoryListings

if getattr(settings, 'CUSTOM_VIEWS', None):
    from django.utils.importlib import import_module
    custom_views = import_module(settings.CUSTOM_VIEWS)
    ListContentType, ObjectDetail = custom_views.ListContentType, custom_views.ObjectDetail
else:
    from ella.core.views import ListContentType, ObjectDetail


res = {
    'ct': r'(?P<content_type>[a-z][a-z0-9-]+)',
    'cat': r'(?P<category>(?:[a-z][a-z0-9-]+/)*[a-z][a-z0-9-]+)',
    'slug': r'(?P<slug>%s)' % slug_re.pattern.strip('^$'),
    'year': r'(?P<year>\d{4})',
    'month': r'(?P<month>\d{1,2})',
    'day': r'(?P<day>\d{1,2})',
    'rest': r'(?P<url_remainder>.+/)',
    'id': r'(?P<id>\d+)',
}

# pre-create views used many times
list_content_type = ListContentType.as_view()
object_detail = ObjectDetail.as_view()

urlpatterns = patterns('',
    # home page
    url(r'^$', list_content_type, name="root_homepage"),

    # list of objects regadless of category and content type
    url(r'^%(year)s/%(month)s/%(day)s/$' % res,
        list_content_type,
        name="list_day"),
    url(r'^%(year)s/%(month)s/$' % res,
        list_content_type,
        name="list_month"),
    url(r'^%(year)s/$' % res,
        list_content_type,
        name="list_year"),

    # object detail
    url(r'^%(cat)s/%(year)s/%(month)s/%(day)s/%(slug)s/$' % res,
        object_detail,
        name="object_detail"),
    url(r'^%(year)s/%(month)s/%(day)s/%(slug)s/$' % res,
        object_detail,
        {'category': ''}, name="home_object_detail"),

    # object detail with custom action
    url(r'^%(cat)s/%(year)s/%(month)s/%(day)s/%(slug)s/%(rest)s$' % res,
        object_detail,
        name="object_detail_action"),
    url(r'^%(year)s/%(month)s/%(day)s/%(slug)s/%(rest)s$' % res,
        object_detail, {'category': ''},
        name="home_object_detail_action"),

    # category listings
    url(r'^%(cat)s/%(year)s/%(month)s/%(day)s/$' % res,
        list_content_type,
        name="category_list_day"),
    url(r'^%(cat)s/%(year)s/%(month)s/$' % res,
        list_content_type,
        name="category_list_month"),
    url(r'^%(cat)s/%(year)s/$' % res,
        list_content_type,
        name="category_list_year"),

    # static detail with custom action
    url(r'^%(cat)s/%(id)s-%(slug)s/%(rest)s$' % res,
        object_detail,
        name='static_detail_action'),
    url(r'^%(id)s-%(slug)s/%(rest)s$' % res,
        object_detail,
        {'category': ''}, name='home_static_detail_action'),

    # static detail
    url(r'^%(cat)s/%(id)s-%(slug)s/$' % res,
        object_detail,
        name='static_detail'),
    url(r'^%(id)s-%(slug)s/$' % res,
        object_detail,
        {'category': ''}, name='home_static_detail'),

    # rss feeds
    url(r'^feeds/$', RSSTopCategoryListings(), name='home_rss_feed'),
    url(r'^feeds/atom/$', AtomTopCategoryListings(), name='home_atom_feed'),
    url(r'^%(cat)s/feeds/$' % res, RSSTopCategoryListings(), name='rss_feed'),
    url(r'^%(cat)s/feeds/atom/$' % res,
        AtomTopCategoryListings(),
        name='atom_feed'),

    # category homepage
    url(r'^%(cat)s/$' % res,
        list_content_type,
        name="category_detail"),

)
