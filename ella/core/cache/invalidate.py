from django.core.cache import cache
from django.contrib.contenttypes.models import ContentType
from django.dispatch import dispatcher
from django.db.models import signals

try:
    import cPickle as pickle
except ImportError:
    import pickle

def parse_message(message):
    '''
    MESSAGE
    destination:/topic/test
    timestamp:1184944814498
    priority:0
    expires:0
    message-id:ID:dev11-42769-1184944719862-3:2:-1:1:3

    XXY
    '''
    lines = message.split('\n')
    if len(lines) < 2 or lines[0] != 'MESSAGE':
        return {}, None

    header = {}
    body = None
    for i in range(1, len(lines)):
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

    def receive(self, message):
        """
        Process message from ActiveMQ
        """
        from ella.core.cache.utils import get_cached_object
        from django.db.models import ObjectDoesNotExist
        header, body = parse_message(message)

        contents = body.split(':', 1)
        if len(contents) != 2 or not contents[0].isdigit() or not contents[1].isdigit():
            return

        try:
            instance = pickle.loads(body)
            self(instance.__class__, instance)
        except:
            pass

    def __call__(self, sender, instance):
        """
        Process post_save signal
        """
        if sender in self._register:
            for key, test in self._register[sender].items():
                if test(instance):
                    cache.delete(key)
                    del self._register[sender][key]

    def register(self, model, test, key):
        self._register.setdefault(model, {})
        self._register[model][key] = test

CACHE_DELETER = CacheDeleter()

def get_propagator(conn):
    def propagate_signal(sender, instance):
        conn.send('/topic/ella', pickle.dumps(instance))
    return propagate_signal

try:
    import stomp
    # initialize connection to ActiveMQ
    conn = stomp.Connection('localhost', 61613)
    # register CD as listener
    conn.addlistener(CACHE_DELETER)
    conn.subscribe('/topic/test')
    conn.start()

    dispatcher.connect(get_propagator(conn), signal=signals.pre_save)
    dispatcher.connect(get_propagator(conn), signal=signals.pre_delete)
except:
    dispatcher.connect(CACHE_DELETER, signal=signals.pre_save)
    dispatcher.connect(CACHE_DELETER, signal=signals.pre_delete)

