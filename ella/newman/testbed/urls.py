from os.path import dirname, join

from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin

import testbed

admin.autodiscover()

urlpatterns = patterns('',)
"""
urlpatterns += patterns('',
    (r'^static/testbed/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': join(dirname(testbed.__file__), 'static'), 'show_indexes': True }),
)

urlpatterns += patterns('',
    (r'^admin/(.*)', admin.site.root),
    (r'^', include('mypage.pages.urls')),
)
"""
