# register custom urls
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _

from ella.core.custom_urls import dispatcher
from ella.ellacomments.views import custom_urls

dispatcher.register(slugify(_('comments')), custom_urls)
