from django.conf.urls.defaults import *
from django.conf import settings

from ella import newman

newman.autodiscover()

import ella
import django

from os.path import dirname, join, normpath

ADMIN_ROOTS = (
        normpath(join(dirname(ella.__file__), 'newman', 'media')),
        normpath(join(dirname(django.__file__), 'contrib', 'admin', 'media')),
)

urlpatterns = patterns('',

    # serve admin media static files
    ( r'^static/admin_media/(?P<path>.*)$', 'ella.utils.views.fallback_serve', {'document_roots': ADMIN_ROOTS} ),
    # serve static files
    ( r'^static/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT, 'show_indexes': True } ),

    # main admin urls
    ('^newman/', include(newman.site.urls)),

    # reverse url lookups
    ( r'^', include('ella.core.urls') ),

)

handler404 = 'ella.core.views.page_not_found'
handler500 = 'ella.core.views.handle_error'



