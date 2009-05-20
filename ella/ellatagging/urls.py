from django.conf.urls.defaults import *
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext # lazy gettext works strange in case of urlpatterns (sometimes doesn't work)

from ella.ellatagging.views import tagged_publishables


urlpatterns = patterns('',
    url(r'^(?P<tag>[\w\s]+)/', tagged_publishables, name="tag_list"),
)
