from django.core.cache import cache
from django.contrib.contenttypes.models import ContentType
from django.dispatch import dispatcher
from django.db.models import signals
from django.conf import settings

try:
    import cPickle as pickle
except ImportError:
    import pickle

def parse_message(message):
    '''
    Parse incomming messages from ActiveMQ

    MESSAGE
    destination:/topic/test
    timestamp:1184944814498
    priority:0
    expires:0
    message-id:ID:dev11-42769-1184944719862-3:2:-1:1:3

    XXY
    '''
    lines = message.split('\n')
    if len(lines) < 3 or lines[1] != 'MESSAGE':
        return {}, None

    header = {}
    body = None
    for i in range(2, len(lines)):
        if lines[i]:
            key, value = lines[i].split(':', 1)
            header[key] = value
        elif i+1 < len(lines):
            body = '\n'.join(lines[i+1:])
            break
        else:
            break

    return header, body

class CacheDeleter(object):
    def __init__(self):
        self._register = {}
        self.signal_handler = self

    def receive(self, message):
        """
        Process message from ActiveMQ
        """
        from ella.core.cache.utils import get_cached_object
        from django.db.models import ObjectDoesNotExist
        header, body = parse_message(message)

        instance = pickle.loads(body)
        # delegate the received signal to __call__
        self(instance.__class__, instance)

    def __call__(self, sender, instance):
        """
        Process pre_save signal
        """
        if sender in self._register:
            for key, test in self._register[sender].items():
                if test(instance):
                    self.invalidate(sender, key)
        return instance

    def invalidate(self, sender, key):
        from ella.core.models import Dependency

        cache.delete(key)
        try:
            del self._register[sender][key]
        except KeyError:
            # we might be racing against ourselves via ActiveMQ
            pass

        # also destroy caches that depend on us
        Dependency.objects.cascade(sender, key)

    def register(self, model, test, key):
        if model not in self._register:
            self._register[model] = {}
            # start listening for the model requested
            dispatcher.connect(self.signal_handler, signal=signals.pre_save, sender=model)
            dispatcher.connect(self.signal_handler, signal=signals.pre_delete, sender=model)
        self._register[model][key] = test

CACHE_DELETER = CacheDeleter()
try:
    ACTIVE_MQ_HOST = settings.ACTIVE_MQ_HOST
except AttributeError:
    raise ImproperlyConfigured, "Please set ACTIVE_MQ_HOST to a valid ActiveMQ Host"

def get_propagator(conn):
    def propagate_signal(sender, instance):
        """
        Trap the pre_save and pre_delete signal and
        invalidate the relative cache entries.
        """
        # notify this instance right away
        CACHE_DELETER(sender, instance)
        # propagate the signal to others
        conn.send('/topic/ella', pickle.dumps(instance))
        return instance
    return propagate_signal

try:
    import stomp
    # initialize connection to ActiveMQ
    conn = stomp.Connection('localhost', 61613)
    # register CD as listener
    conn.addlistener(CACHE_DELETER)
    conn.subscribe('/topic/ella')
    conn.start()
    # give it time to form a connection
    import time
    time.sleep(2)
    # register to close the activeMQ connection on exit
    import atexit
    atexit.register(conn.disconnect)
    # register the proper propagation function for intercepting the proper signals
    CACHE_DELETER.signal_handler = get_propagator(conn)
except:
    pass
    # TODO: log warning, that we are running without ActiveMQ

