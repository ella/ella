from django.conf.urls.defaults import *

from ella.ratings.views import *

urlpatterns = patterns('',
    # for finer-grained system, use plusminus
    url(r'^rate/(?P<content_type_id>\d+)/(?P<object_id>\d+)/up/$', rate, {'plusminus' : 1}, name='rate_up'),
    url(r'^rate/(?P<content_type_id>\d+)/(?P<object_id>\d+)/down/$', rate, {'plusminus' : -1}, name='rate_down'),
)
