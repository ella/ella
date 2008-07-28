from django.conf.urls.defaults import *
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext # lazy gettext works strange in case of urlpatterns (sometimes doesn't work)

from ella.tagging.views import tagged_publishables


urlpatterns = patterns('',
    url(r'^(?P<tag>[\w\s]+)/', tagged_publishables, name="tag_list"),

    # TODO delete following mess:
    # url(r'^%s/$' % slugify(gettext('Tags')), 'django.views.generic.simple.direct_to_template', {'template': 'tagging/tags_cloud.html'}, name="tags_cloud"),
    # url(r'^%s/(?P<tag>[^/]+)/$' % slugify(ugettext('Tags')), tag_list_for_model, name="tag_list"),
    # url(r'^%s/(?P<tag>[^/]+)/(?P<model>[^/]+)/$' % slugify(ugettext('Tags')), tag_list_for_model, name="tag_model_list"),
)
