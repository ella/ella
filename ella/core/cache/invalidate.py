from django.core.cache import cache
from django.contrib.contenttypes.models import ContentType
from django.dispatch import dispatcher
from django.db.models import signals
from django.conf import settings
from django.utils.datastructures import MultiValueDict

try:
    import cPickle as pickle
except ImportError:
    import pickle

class CacheDeleter(object):
    def __init__(self):
        self._register = {}
        self.signal_handler = self

    def on_error(self, header, message):
        pass

    def on_message(self, header, body):
        """
        Process message from ActiveMQ
        """
        instance = pickle.loads(body)

        # delegate the received signal to __call__
        self(instance.__class__, instance)

    def __call__(self, sender, instance):
        """
        Process pre_save signal
        """
        if sender in self._register:
            pks, tests = self._register[sender]
            if instance._get_pk_val() in pks:
                for key in pks.getlist(instance._get_pk_val()):
                    self.invalidate(sender, key, from_test=False)
                del pks[instance._get_pk_val()]

            for key in tests.keys():
                for t in tests.getlist(key):
                    if t(instance):
                        self.invalidate(sender, key)
                        del tests[key]
                        break
        return instance

    def invalidate(self, sender, key, from_test=True):
        from ella.core.models import Dependency

        cache.delete(key)
        # also destroy caches that depend on us

        Dependency.objects.cascade(sender, key)

    def register_model(self, model):
        if model not in self._register:
            self._register[model] = (MultiValueDict(), MultiValueDict())
            # start listening for the model requested
            dispatcher.connect(self.signal_handler, signal=signals.pre_save, sender=model)
            dispatcher.connect(self.signal_handler, signal=signals.pre_delete, sender=model)

    def register_test(self, model, test, key):
        self.register_model(model)
        self._register[model][1].appendlist(key, test)

    def register_pk(self, instance, key):
        self.register_model(instance.__class__)
        self._register[instance.__class__][0].appendlist(instance._get_pk_val(), key)


CACHE_DELETER = CacheDeleter()
ACTIVE_MQ_HOST = getattr(settings, 'ACTIVE_MQ_HOST', None)
ACTIVE_MQ_PORT = getattr(settings, 'ACTIVE_MQ_PORT', 61613)

def get_propagator(conn):
    def propagate_signal(sender, instance):
        """
        Trap the pre_save and pre_delete signal and
        invalidate the relative cache entries.
        """
        # notify this instance right away
        CACHE_DELETER(sender, instance)
        try:
            # propagate the signal to others
            conn.send(pickle.dumps(instance), destination='/topic/ella')
        except:
            pass
        return instance
    return propagate_signal

try:
    import stomp

    # initialize connection to ActiveMQ
    conn = stomp.Connection([(ACTIVE_MQ_HOST, ACTIVE_MQ_PORT)], '', '')

    # register CD as listener
    conn.add_listener(CACHE_DELETER)

    conn.start()
    conn.connect()
    conn.subscribe(destination='/topic/ella')

    # register to close the activeMQ connection on exit
    import atexit
    atexit.register(conn.disconnect)

    # register the proper propagation function for intercepting the proper signals
    CACHE_DELETER.signal_handler = get_propagator(conn)
except:
    pass
    # TODO: log warning, that we are running without ActiveMQ

