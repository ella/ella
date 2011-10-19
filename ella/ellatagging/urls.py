from django.conf.urls.defaults import *
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext # lazy gettext works strange in case of urlpatterns (sometimes doesn't work)

from ella.ellatagging.views import TaggedPublishablesView


urlpatterns = patterns('',
    url(r'^(?P<tag>[\w\s]+)/', TaggedPublishablesView.as_view(), name="tag_list"),
)
