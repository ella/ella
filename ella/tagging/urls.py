from django.conf.urls.defaults import *
from django.utils.translation import ugettext # lazy gettext works strange in case of urlpatterns (sometimes doesn't work)

from ella.tagging.views import tagged_publishables

urlpatterns = patterns('',
    url(r'^%s/(?P<tag_name>[\w\s]+)/' % ugettext('tagged'), tagged_publishables, name="tagged_publishables"),
)
