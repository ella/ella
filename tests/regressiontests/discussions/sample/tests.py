# --- doc tests for discussions app ---
import logging.config
from settings import *
logging.config.fileConfig(LOGGING_CONFIG_FILE)
logging.getLogger('ella.discussions').error('AHOOOOOOOJ')

banned_strings = r"""
>>> from ella.discussions.models import *
>>> from ella.discussions.views import *
>>> filter_banned_strings(u'A b prdel c d.')
u'A b *** c d.'

>>> filter_banned_strings(u'A b prdel c kurva d.')
u'A b *** c *** d.'

>>> filter_banned_strings(u'A b prdel c kurvaprdel d.')
u'A b *** c ****** d.'

>>> filter_banned_strings(u'A b kujvapudel d.')
u'A b kujvapudel d.'

"""


__test__ = {
    'discussions_filter_banned_strings': banned_strings,
}

