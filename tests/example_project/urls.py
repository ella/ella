from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from ella import newman
from ella import ellaadmin
from ella.utils import installedapps

newman.autodiscover()
admin.autodiscover()
installedapps.init_logger()

urlpatterns = patterns('',
    # serve media files
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT, 'show_indexes': True }),

    url(r'^exports/', include('ella.ellaexports.urls')),

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

urlpatterns += staticfiles_urlpatterns()
handler404 = 'ella.core.views.page_not_found'
handler500 = 'ella.core.views.handle_error'
