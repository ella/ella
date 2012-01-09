from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings

import ella

from os.path import dirname, join, normpath

ADMIN_ROOTS = (
    normpath(join(dirname(ella.__file__), 'newman', 'static', 'newman')),
)

urlpatterns = patterns('',
    (r'^tags/', include('ella.ellatagging.urls')),
    (r'^polls/', include('ella.polls.urls')),
    (r'^', include('ella.core.urls')),
    (r'^%s/(?P<path>.*)$' % settings.NEWMAN_MEDIA_PREFIX.strip('/'), 'ella.utils.views.fallback_serve', {'document_roots': ADMIN_ROOTS}),
)
