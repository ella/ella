from django.conf.urls.defaults import patterns, include

urlpatterns = patterns('',
    (r'^', include('ella.core.urls')),
)
