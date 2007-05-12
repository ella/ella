from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    # (r'^authtests/', include('authtests.foo.urls')),

    # Uncomment this for admin:
     (r'^', include('auth_sample.urls')),
)
