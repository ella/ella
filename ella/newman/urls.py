from django.conf.urls.defaults import *

urlpatterns = patterns('ella.newman.views',

    # send err report / feature request
    url(r'^err-report/$', 'err_report', name="newman-err-report"),
)
