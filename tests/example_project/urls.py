from os.path import dirname, join, normpath

import django
from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin

import ella
from ella import newman
from ella import ellaadmin
from ella.utils import installedapps


newman.autodiscover()
admin.autodiscover()
installedapps.init_logger()


ADMIN_ROOTS = (
    normpath(join(dirname(ella.__file__), 'newman', 'media')),
    normpath(join(dirname(django.__file__), 'contrib', 'admin', 'media')),
)

js_info_dict = {
    'packages': ('ella.newman',),
}

urlpatterns = patterns('',

    # serve admin media static files
    url(r'^feeds/mrss/slug/(?P<slug>[a-z0-9-/]+)/$', 'ella.exports.views.mrss_exports', name='ella_exports_by_slug'),
    #(r'^feeds/mrss/(?P<category>[a-z0-9-/]+)/(?P<content_type>[a-z0-9-]+)/$', 'ella.exports.views.mrss_exports'),
    url(r'^feeds/mrss/(?P<category>[a-z0-9-/]*)/$', 'ella.exports.views.mrss_exports', name='ella_exports_by_category'),
    #(r'^feeds/mrss/(?P<category>.*)$', 'ella.exports.views.mrss_exports'),
    (r'^static/newman_media/(?P<path>.*)$', 'ella.utils.views.fallback_serve', {'document_roots': ADMIN_ROOTS}),
    (r'^static/admin_media/(?P<path>.*)$', 'ella.utils.views.fallback_serve', {'document_roots': ADMIN_ROOTS}),

    # serve static files
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT, 'show_indexes': True }),

    # newman JS translations
    (r'^newman/jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),

    # main admin urls
    ('^newman/', include(newman.site.urls)),
    ('^admin/', include(ellaadmin.site.urls)),

    # polls urls
    ('^polls/', include('ella.polls.urls')),

    # tagging
    url(r'^tagging/', include('ella.ellatagging.urls')),

    # reverse url lookups
    (r'^', include('ella.core.urls')),

)

handler404 = 'ella.core.views.page_not_found'
handler500 = 'ella.core.views.handle_error'
