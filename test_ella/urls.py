from django.conf.urls.defaults import *

import ella

from os.path import dirname, join, normpath

ADMIN_ROOTS = (
    normpath(join(dirname(ella.__file__), 'newman', 'static', 'newman')),
)

urlpatterns = patterns('',
    (r'^tags/', include('ella.ellatagging.urls')),
    (r'^polls/', include('ella.polls.urls')),
    (r'^', include('ella.core.urls')),
)
