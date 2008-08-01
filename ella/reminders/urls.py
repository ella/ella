from django.conf.urls.defaults import *
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _

from ella.reminders.views import *

urlpatterns = patterns('',
    url('^$', reminder_list),
    url('^(?P<reminder_class>[a-z0-9-]+)/$', reminder_instances_list),
    url('^(?P<reminder_class>[a-z0-9-]+)/(?P<reminder>[a-z0-9-]+)/$', reminder_detail),
    url('^(?P<reminder_class>[a-z0-9-]+)/(?P<reminder>[a-z0-9-]+)/%s/$' % slugify(_('subscribe')), reminder_subscribe),
    url('^(?P<reminder_class>[a-z0-9-]+)/(?P<reminder>[a-z0-9-]+)/%s/$' % slugify(_('unsubscribe')), reminder_unsubscribe),
    url('^(?P<reminder_class>[a-z0-9-]+)/(?P<reminder>[a-z0-9-]+)/(?P<event>[a-z0-9-]+)/$', event_detail, name='event_detail'),
    url('^(?P<reminder_class>[a-z0-9-]+)/(?P<reminder>[a-z0-9-]+)/(?P<event>[a-z0-9-]+)/(?P<url_remainder>.*)/$', event_detail, name='event_detail_action'),
)
