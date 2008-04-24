# register admin options
from ella.core import admin

# add some of our templatetags to builtins
from ella.core import templatetags

# import the invalidator to initiate a connection to the ActiveMQ server
from ella.core.cache import invalidate
