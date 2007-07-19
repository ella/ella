from django.conf.urls.defaults import *

from ella.ratings.views import *

urlpatterns = patterns('',
    # for finer-grained system, use plusminus
    url(r'^rate/up/$', rate, {'plusminus' : 1}, name='rate_up'),
    url(r'^rate/down/$', rate, {'plusminus' : -1}, name='rate_down'),
)
