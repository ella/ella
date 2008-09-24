from django.http import Http404
from django.conf.urls.defaults import *
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _

from ella.core.custom_urls import dispatcher
from ella.ratings.views import rate

dispatcher.register(_('rate'),  rate)

# Rate up and rate down methods are currently not used
# and are untested so are commented out
urlpatterns = patterns('',
    # for finer-grained system, use plusminus
#    url(r'^rate/up/$', rate, {'plusminus' : 1}, name='rate_up'),
#    url(r'^rate/down/$', rate, {'plusminus' : -1}, name='rate_down'),
)
