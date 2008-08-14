from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _

from ella.core.custom_urls import dispatcher
from ella.sendmail.views import sendmail_custom_urls

dispatcher.register(slugify(_('send mail')), sendmail_custom_urls)
