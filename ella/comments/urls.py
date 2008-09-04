from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _

from ella.core.custom_urls import dispatcher

dispatcher.register(slugify(_('comments')), comments_custom_urls)

