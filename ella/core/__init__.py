from django.utils.translation import ugettext_lazy as _
trans_app_label = _('Core')

# add some of our templatetags to builtins
from ella.core import templatetags

# give RedisListingHandler a chance to register it's signals
from ella.core.cache import redis
del redis

