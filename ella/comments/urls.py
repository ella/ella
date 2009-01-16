from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _

from ella.core.custom_urls import dispatcher
from ella.comments.views import comments_custom_urls

dispatcher.register(slugify(_('comments')), comments_custom_urls)

