from django.conf.urls.defaults import *
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _
from django.conf import settings

urlpatterns = patterns( '',
    url(r'^aggregated/(?P<slug>.*)/$', 'ella.ellaexports.views.aggregated_export', name='ella_exports_aggregated_by_slug'),
    url(r'^(?P<slug>.*)/$', 'ella.ellaexports.views.mrss_export', name='ella_exports_by_slug'),
)
