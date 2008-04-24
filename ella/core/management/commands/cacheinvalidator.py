try:
    import cPickle as pickle
except ImportError:
    import pickle

import time
import logging
import stomp
from django.core.cache import cache
from django.core.management.base import BaseCommand, CommandError
from django.utils.datastructures import MultiValueDict
from django.conf import settings

log = logging.getLogger('cache')

AMQ_DESTINATION = '/topic/ella'

class CacheInvalidator(object):
    def __init__(self):
        self._register = {}
        self._dependencies = {}

    def on_error(self, headers, message):
        log.error('ActiveMQ/Stomp on_error')
        print 'received an error %s' % message

    def on_disconnected(self):
        log.error('CI: Connection was lost!')

    def on_message(self, headers, message):
        " Process message from ActiveMQ "

        type = headers['type']
        key = headers['key']

        # debug
        log.debug('CI: I received a message type %s' % type)

        if type == 'pk':
            inst = pickle.loads(message)
            self.append_pk(inst, key)
        elif type == 'test':
            model = headers['model']
            self.append_test(model, message, key)
        elif type == 'del':
            inst = pickle.loads(message)
            self.run(inst.__class__, inst)
        elif type == 'dep':
            model = headers['model']
            self.register_dependency(key, model)

    def append_model(self, model):
        " Append model to _registry "

        if model not in self._register:
            self._register[model] = (MultiValueDict(), MultiValueDict())

    def append_test(self, model, test, key):
        " Append invalidation test to _registry "

        self.append_model(model)
        self._register[model][1].appendlist(key, test)

    def append_pk(self, instance, key):
        " Append PK to _registry "

        self.append_model(instance.__class__)
        self._register[instance.__class__][0].appendlist(instance._get_pk_val(), key)

    def register_dependency(self, src_key, dst_key):
        if src_key not in self._dependencies:
            self._dependencies[src_key] = list()
        self._dependencies[src_key].append(dst_key)

    def _check_test(self, instance, test_str):
        " Check test params on instance "

        if not test_str:
            return True

        # Parse string
        for subtest in test_str.split(';'):
            attr = subtest.split(':')
            if not (instance.getattr(instance, attr[0].strip()) == attr[1].strip()):
                return False
        return True

    def run(self, sender, instance):
        " Process cache invalidation PKs and tests "

        if sender in self._register:
            pks, tests = self._register[sender]
            if instance._get_pk_val() in pks:
                for key in pks.getlist(instance._get_pk_val()):
                    self.invalidate(sender, key, from_test=False)
                del pks[instance._get_pk_val()]

            for key in tests.keys():
                for t in tests.getlist(key):
                    if self._check_test(instance, t):
                        self.invalidate(sender, key)
                        del tests[key]
                        break
#        return instance

    def invalidate(self, sender, key, from_test=True):
        " Invaidate cache "
        cache.delete(key)
        # also destroy caches that depend on us
        log.debug('Invalidate key "%s".' % key)

        # Process cache dependencies
        if key in self._dependencies.keys():
            for dst in self._dependencies[key]:
                log.debug('Dependency invalidate key "%s".' % dst)
                cache.delete(dst)
            del self._dependencies[key]


ACTIVE_MQ_HOST = getattr(settings, 'ACTIVE_MQ_HOST', None)
ACTIVE_MQ_PORT = getattr(settings, 'ACTIVE_MQ_PORT', 61613)

class Command(BaseCommand):
    help = 'Run cache invalidator.'

    def handle(self,  *ct_names, **options):

        if not ACTIVE_MQ_HOST:
            raise CommandError('ActiveMQ host not defined!')

        try:

            # initialize connection for CI
            conn = stomp.Connection([(ACTIVE_MQ_HOST, ACTIVE_MQ_PORT)])
            conn.add_listener(CacheInvalidator())
            conn.start()
            conn.connect()
            conn.subscribe(destination=AMQ_DESTINATION, ack='auto')
            log.info('CI now listen on "%s"' % AMQ_DESTINATION)

            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            conn.unsubscribe(destination=AMQ_DESTINATION)
            conn.stop()
            log.info('Connection was closed...')

        except:
            raise CommandError('Can not initialize stomp connection!')
