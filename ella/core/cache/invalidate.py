try:
    import cPickle as pickle
except ImportError:
    import pickle

import logging
from django.dispatch import dispatcher
from django.db.models import signals
from django.conf import settings
from django.core.cache import cache


log = logging.getLogger('cache')

CACHE_TIMEOUT = getattr(settings, 'CACHE_TIMEOUT', 10*60)
AMQ_DESTINATION = getattr(settings, 'CI_AMQ_DESTINATION', '/topic/ella')
AMQ_HOST = getattr(settings, 'ACTIVE_MQ_HOST', None)
AMQ_PORT = getattr(settings, 'ACTIVE_MQ_PORT', 61613)

def load_cache_deleter(cache_deleter=None):
    '''
    Loads cache deleter (invalidator) and calls its method connect.
    '''
    if cache_deleter is None:
        cache_deleter = 'ella.core.cache.invalidate.CacheDeleterCache'

    from django.utils.importlib import import_module
    path, obj_name = cache_deleter.rsplit('.', 1)
    module = import_module(path)
    deleter =  getattr(module, obj_name)()
    if hasattr(deleter, 'connect'):
        deleter.connect()
    return deleter


class MsgWrapper(object):
    pass

class CacheDeleterAmq(object):
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
        self._send(test, 'test', key, model)

    def register_pk(self, instance, key):
        msg = pickle.dumps(instance)
        self._send(msg, 'pk', key)

    def register_dependency(self, src_key, obj_key):
        self._send('', 'dep', src_key, obj_key)

    def propagate_signal(self, sender, instance):
        """
        Trap the pre_save and pre_delete signal and
        invalidate the relative cache entries.
        """
        # log about received signal
        log.debug('Signal from "%s" received.' % sender)
        try:
            # propagate the signal to Cache Invalidator
            self._send(pickle.dumps(instance), 'del')
        except:
            log.error('Can not send message to AMQ.')

    def connect(self, *args, **kwargs):

        # initialize connection to ActiveMQ
        self.conn = stomp.Connection(*args, **kwargs)
        self.conn.start()
        self.conn.connect()

    def disconnect(self):
        self.conn.stop()


class CacheDeleterCache(object):

    def connect(self):
        signals.post_save.connect(self._signal_handler)
        signals.post_delete.connect(self._signal_handler)

    @staticmethod
    def _get_key(obj):
        from hashlib import md5
        return md5(repr(('ella.core.cache.invalidate.CacheDeleterCache', obj.__class__, obj.pk,))).hexdigest()

    def _signal_handler(self, sender, **kwargs):
            self.clear_for_obj(kwargs['instance'])

    def register_pk(self, obj, key):
        self._append_key(obj, key)

    def register_test(self, model, test, key):
        pass

    def clear_for_obj(self, obj):
        for key in self.get_keys(obj):
            cache.delete(key)
        cache.delete(self._get_key(obj))

    def get_keys(self, obj):
        return self._get_obj(obj).split('/')

    def _append_key(self, obj, key):
        self._set_obj(obj, self._get_obj(obj) + '/' + key)

    def _get_obj(self, obj):
        ret = cache.get(self._get_key(obj), '')
        return ret

    def _set_obj(self, obj, data):
        cache.set(self._get_key(obj), data, CACHE_TIMEOUT)

    def register_dependency(self, src_key, obj_key):
        pass


CACHE_DELETER = load_cache_deleter(getattr(settings, 'ELLA_CACHE_DELETER', None))

if AMQ_HOST and isinstance(CACHE_DELETER, CacheDeleterAmq):
    try:
        import stomp
        import socket

        # check connection to defined AMQ
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((AMQ_HOST, AMQ_PORT))
        s.close()

        # connection checked, connect CACHE_DELETER
        CACHE_DELETER.connect([(AMQ_HOST, AMQ_PORT)])

        # start listening for any model
        dispatcher.connect(CACHE_DELETER.propagate_signal, signal=signals.post_save)
        dispatcher.connect(CACHE_DELETER.propagate_signal, signal=signals.post_delete)
        log.debug('Start listening for any model')
    except:
        log.warning('ActiveMQ not running')

