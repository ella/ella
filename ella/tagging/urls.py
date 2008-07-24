from django.conf.urls.defaults import *
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext # lazy gettext works strange in case of urlpatterns (sometimes doesn't work)

from ella.tagging.views import tagged_publishables


urlpatterns = patterns('',
    url(r'^%s/(?P<tag>[\w\s]+)/' % slugify(ugettext('tagged')), tagged_publishables, name="tag_list"),
    #url(r'^%s/(?P<tag>[^/]+)/$' % slugify(ugettext('Tags')), tag_list_for_model, name="tag_list"),
    #url(r'^%s/(?P<tag>[^/]+)/(?P<model>[^/]+)/$' % slugify(ugettext('Tags')), tag_list_for_model, name="tag_model_list"),
)
