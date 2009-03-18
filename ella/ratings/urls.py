from django.utils.translation import ugettext as _

from ella.core.custom_urls import dispatcher
from ella.ratings.views import rate

dispatcher.register(_('rate'),  rate)
