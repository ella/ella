from django.http import Http404
from django.conf.urls.defaults import *
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _

from ella.core.custom_urls import dispatcher
from ella.ratings.views import rate, rate_by_value

dispatcher.register('rate',  rate)
dispatcher.register(slugify(_('rate by value')),  rate_by_value)

urlpatterns = patterns('',
    # for finer-grained system, use plusminus
    url(r'^rate/up/$', rate, {'plusminus' : 1}, name='rate_up'),
    url(r'^rate/down/$', rate, {'plusminus' : -1}, name='rate_down'),
    url(r'^%s/$' % slugify(_('rate by value')), rate, name='rate by value'),
)
