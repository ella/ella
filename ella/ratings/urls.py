from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify
from django.conf.urls.defaults import patterns, url

from ella.core.custom_urls import resolver
from ella.ratings.views import rate

resolver.register(
    patterns('',
        url('^$', rate, name='ratings-rate'),
    ), prefix=slugify(_('rate'))
)
