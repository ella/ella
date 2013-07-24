from django.contrib import admin
from django.conf import settings

try:
    from django.conf.urls import *
except ImportError:
    from django.conf.urls.defaults import *

from test_ella.urls import urlpatterns

admin.autodiscover()

urlpatterns = patterns('',
    (r'^%s(?P<path>.*)$' % (settings.MEDIA_URL.lstrip('/')), 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT, }),
    (r'^admin/', include(admin.site.urls)),
) + urlpatterns
