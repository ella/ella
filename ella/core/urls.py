from django.conf import settings
from django.core.validators import slug_re
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

try:
    from django.conf.urls import patterns, include, url
except ImportError:
    from django.conf.urls.defaults import patterns, include, url

from ella.core.views import object_detail, list_content_type, category_detail, \
                            home, AuthorView


try:
    if settings.CUSTOM_VIEWS:
        views = settings.VIEWS
        temp = __import__(views, globals(), locals(), ['object_detail', 'list_content_type', 'category_detail', 'home', 'AuthorView'])
        object_detail = temp.object_detail
        list_content_type = temp.list_content_type
        category_detail = temp.category_detail
        home = temp.home
        AuthorView = temp.AuthorView
except:
    pass

from ella.core.feeds import RSSTopCategoryListings, AtomTopCategoryListings


res = {
    'ct': r'(?P<content_type>[a-z][a-z0-9-]+)',
    'cat': r'(?P<category>(?:(?:[0-9]+[^0-9-]|[a-z])[a-z0-9-]*/)*(?:[0-9]+[^0-9-]|[a-z])[a-z0-9-]*)',
    'slug': r'(?P<slug>%s)' % slug_re.pattern.strip('^$'),
    'year': r'(?P<year>\d{4})',
    'month': r'(?P<month>\d{1,2})',
    'day': r'(?P<day>\d{1,2})',
    'rest': r'(?P<url_remainder>.+/)',
    'id': r'(?P<id>\d+)',
    'author': slugify(_('author'))
}

urlpatterns = patterns('',
    # home page
    url(r'^$', home, name="root_homepage"),

    # author detail
    url(r'^%(author)s/%(slug)s/$' % res, AuthorView.as_view(), name='author_detail'),

    # export banners
    url(r'^export/xml/(?P<name>[a-z0-9-]+)/$', 'ella.core.views.export', { 'count' : 3, 'content_type' : 'text/xml' }, name="named_export_xml"),
    url(r'^export/$', 'ella.core.views.export', { 'count' : 3 }, name="export"),
    url(r'^export/(?P<name>[a-z0-9-]+)/$', 'ella.core.views.export', { 'count' : 3 }, name="named_export"),

    # list of objects regadless of category and content type
    url(r'^%(year)s/%(month)s/%(day)s/$' % res, list_content_type, name="list_day"),
    url(r'^%(year)s/%(month)s/$' % res, list_content_type, name="list_month"),
    url(r'^%(year)s/$' % res, list_content_type, name="list_year"),

    # object detail
    url(r'^%(cat)s/%(year)s/%(month)s/%(day)s/%(slug)s/$' % res, object_detail, name="object_detail"),
    url(r'^%(year)s/%(month)s/%(day)s/%(slug)s/$' % res, object_detail, { 'category' : '' }, name="home_object_detail"),

    # object detail with custom action
    url(r'^%(cat)s/%(year)s/%(month)s/%(day)s/%(slug)s/%(rest)s$' % res, object_detail, name="object_detail_action"),
    url(r'^%(year)s/%(month)s/%(day)s/%(slug)s/%(rest)s$' % res, object_detail, { 'category' : '' }, name="home_object_detail_action"),

    # category listings
    url(r'^%(cat)s/%(year)s/%(month)s/%(day)s/$' % res, list_content_type, name="category_list_day"),
    url(r'^%(cat)s/%(year)s/%(month)s/$' % res, list_content_type, name="category_list_month"),
    url(r'^%(cat)s/%(year)s/$' % res, list_content_type, name="category_list_year"),

    # static detail with custom action
    url(r'^%(cat)s/%(id)s-%(slug)s/%(rest)s$' % res, object_detail, name='static_detail_action'),
    url(r'^%(id)s-%(slug)s/%(rest)s$' % res, object_detail, { 'category' : '' }, name='home_static_detail_action'),

    # static detail
    url(r'^%(cat)s/%(id)s-%(slug)s/$' % res, object_detail, name='static_detail'),
    url(r'^%(id)s-%(slug)s/$' % res, object_detail, { 'category' : '' }, name='home_static_detail'),

    # rss feeds
    url(r'^feeds/$', RSSTopCategoryListings(), name='home_rss_feed'),
    url(r'^feeds/atom/$', AtomTopCategoryListings(), name='home_atom_feed'),
    url(r'^%(cat)s/feeds/$' % res, RSSTopCategoryListings(), name='rss_feed'),
    url(r'^%(cat)s/feeds/atom/$' % res, AtomTopCategoryListings(), name='atom_feed'),

    # category homepage
    url(r'^%(cat)s/$' % res, category_detail, name="category_detail"),

)
