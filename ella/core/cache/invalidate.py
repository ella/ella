try:
    import cPickle as pickle
except ImportError:
    import pickle

from django.dispatch import dispatcher
from django.db.models import signals
from django.conf import settings

import logging
log = logging.getLogger('cache')
AMQ_DESTINATION = '/topic/ella'


class CacheDeleter(object):
    def __init__(self):
        self.signal_handler = self
        self.conn = None

    def on_error(self, header, message):
        " Log AMQ/stomp error message "
        log.error('AMQ: %s' % header)

    def on_disconnected(self):
        log.error('AMQ: Connection was lost!')

    def _send(self, msg, type, key=None, model=None):
        " Send message to AMQ "
        if self.conn:
            headers = {'Type': type, 'Key': key, 'Model': model}
            self.conn.send(msg, headers=headers, destination=AMQ_DESTINATION)

    def register_test(self, model, test, key):
        self._send(test, 'test', key, model.__class__)

    def register_pk(self, instance, key):
        msg = pickle.dumps(instance)
        self._send(msg, 'pk', key)

    def register_dependency(self, src_key, obj_key):
        self._send('', 'dep', src_key, obj_key)


CACHE_DELETER = CacheDeleter()
ACTIVE_MQ_HOST = getattr(settings, 'ACTIVE_MQ_HOST', None)
ACTIVE_MQ_PORT = getattr(settings, 'ACTIVE_MQ_PORT', 61613)

def get_propagator(conn):
    def propagate_signal(sender, instance):
        """
        Trap the pre_save and pre_delete signal and
        invalidate the relative cache entries.
        """
        try:
            # propagate the signal to Cache Invalidator
            conn.send(pickle.dumps(instance), headers={'Type':'del','Key':None,'Test':None}, destination=AMQ_DESTINATION)
            log.debug('TO AMQ: %s' % instance)
        except:
            log.error('Can not send message to AMQ.')
        return instance
    return propagate_signal


if ACTIVE_MQ_HOST:
    try:
        import stomp

        # initialize connection to ActiveMQ
        conn = stomp.Connection([(ACTIVE_MQ_HOST, ACTIVE_MQ_PORT)])
        conn.start()
        conn.connect()

        # register to close the activeMQ connection on exit
        import atexit
        atexit.register(conn.disconnect)

        # register the proper propagation function for intercepting the proper signals
        CACHE_DELETER.signal_handler = get_propagator(conn)
        CACHE_DELETER.conn = conn

        # start listening for any model
        dispatcher.connect(CACHE_DELETER.signal_handler, signal=signals.pre_save)
        dispatcher.connect(CACHE_DELETER.signal_handler, signal=signals.pre_delete)
        log.debug('Start listening for any model')

    except:
        log.warning('ActiveMQ not running')