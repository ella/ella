from django.conf.urls.defaults import *
from django.contrib import admin
from django import VERSION


if VERSION[2] == 'newforms-admin':
    urlpatterns = patterns('',
        # NewformsAdminBranch
        ('^admin/(.*)', admin.site.root),
        (r'^comments/', include('ella.comments.urls')),
        (r'^test/', include('komments.sample.urls')),
)
else:
    urlpatterns = patterns('',
        # Uncomment this for admin:
        (r'^admin/', include('django.contrib.admin.urls')),
)

