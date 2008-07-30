from django.conf.urls.defaults import *

# Uncomment this for admin:
from django.contrib import admin

urlpatterns = patterns('',
    # Example:
     (r'^reminders/', include('ella.reminders.urls')),

    # Uncomment this for admin:
    ('^admin/(.*)', admin.site.root),
)

admin.autodiscover()
