try:
    import cPickle as pickle
except ImportError:
    import pickle

import time
import logging
import stomp
import socket
from django.core.cache import cache
from django.core.management.base import BaseCommand, CommandError
from django.utils.datastructures import MultiValueDict
from django.conf import settings


log = logging.getLogger('cache')

AMQ_DESTINATION = getattr(settings, 'CI_AMQ_DESTINATION', '/topic/ella')
AMQ_HOST = getattr(settings, 'ACTIVE_MQ_HOST', None)
AMQ_PORT = getattr(settings, 'ACTIVE_MQ_PORT', 61613)

REGISTER_KEY = getattr(settings, 'CI_REGISTER_KEY', 'ella_ci_register')
DEPS_KEY = getattr(settings, 'CI_DEPS_KEY', 'ella_ci_deps')


class CacheInvalidator(object):
    def __init__(self):
        self._register = self._register_get()
        self._dependencies = self._dependencies_get()

    def _register_get(self):
        r = cache.get(REGISTER_KEY)
        if not r:
            return {}
        log.info('CI: I have loaded existing register from cache.')
        return r

    def _register_save(self):
        cache.set(REGISTER_KEY, self._register)

    def _dependencies_get(self):
        d = cache.get(DEPS_KEY)
        if not d:
            return {}
        log.info('CI: I have loaded existing dependencies from cache.')
        return d

    def _dependencies_save(self):
        cache.set(DEPS_KEY, self._dependencies)

    def on_error(self, headers, message):
        log.error('ActiveMQ/Stomp on_error')

    def on_disconnected(self):
        log.error('CI: Connection was lost!')

    def on_message(self, headers, message):
        " Process message from ActiveMQ "

        type = headers['type']
        key = headers['key']

        if type == 'pk':
            self.append_pk(pickle.loads(message), key)
        elif type == 'test':
            self.append_test(headers['model'], message, key)
        elif type == 'del':
            self.run(pickle.loads(message))
        elif type == 'dep':
            self.register_dependency(key, headers['model'])

    def append_model(self, model):
        " Append model to _registry "

        if model not in self._register:
            self._register[model] = (MultiValueDict(), MultiValueDict())
            log.debug('CI appended model: %s' % model)

    def append_test(self, model, test, key):
        " Append invalidation test to _registry "

        self.append_model(model)
        self._register[model][1].appendlist(key, test)
        self._register_save()
        log.debug('CI appended test - model: %s, test: %s, key: %s' % (model, test, key))

    def append_pk(self, instance, key):
        " Append PK to _registry "

        # We need key for _register as string
        modelkey = str(instance.__class__)
        self.append_model(modelkey)
        self._register[modelkey][0].appendlist(instance._get_pk_val(), key)
        self._register_save()
#        log.debug('CI appended PK, model: %s, pk: %s, key: %s' % (instance.__class__, instance._get_pk_val(), key))

    def register_dependency(self, src_key, dst_key):
        if src_key not in self._dependencies:
            self._dependencies[src_key] = list()
        self._dependencies[src_key].append(dst_key)
        self._dependencies_save()
        log.debug('CI register dependency, src: %s, dst: %s' % (src_key, dst_key))

    def _check_test(self, instance, test_str):
        " Check test params on instance "

        log.debug('Trying test "%s" for %s.' % (test_str, instance))

        if not test_str:
            return True

        # Parse string
        for subtest in test_str.split(';'):
            attr = subtest.split(':')
            if not (str(instance.__getattribute__(attr[0].strip())) == attr[1].strip()):
                return False
        log.debug('CI True test(s) %s on %s.' % (test_str, instance))
        return True

    def run(self, instance):
        " Process cache invalidation PKs and tests "

        sender = str(instance.__class__)

        log.debug('CI start processing invalidation sender: %s, inst: %s.' % (sender, instance))

        if sender in self._register:
            log.debug('CI Sender %s is in _register.' % sender)
            pks, tests = self._register[sender]
            if instance._get_pk_val() in pks:
                for key in pks.getlist(instance._get_pk_val()):
                    self.invalidate(sender, key, from_test=False)
                del pks[instance._get_pk_val()]
                self._register_save()

            for key in tests.keys():
                for t in tests.getlist(key):
                    if self._check_test(instance, t):
                        self.invalidate(sender, key)
                        del tests[key]
                        self._register_save()
                        break

    def invalidate(self, sender, key, from_test=True):
        " Invaidate cache "
        cache.delete(key)
        log.debug('CI invalidate key "%s".' % key)

        # Process cache dependencies
        if key in self._dependencies.keys():
            for dst in self._dependencies[key]:
                log.debug('CI dependency invalidate key "%s".' % dst)
                cache.delete(dst)
            del self._dependencies[key]
            self._dependencies_save()


class Command(BaseCommand):
    help = 'Run cache invalidator.'

    def handle(self,  *ct_names, **options):

        if not AMQ_HOST:
            raise CommandError('ActiveMQ host not defined!')

        try:
            # check connection to defined AMQ
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((AMQ_HOST, AMQ_PORT))
            s.close()
        except:
            raise CommandError('Can\'t connect to defined AMQ server %s:%s!' % (AMQ_HOST, AMQ_PORT))

        try:
            # initialize connection for CI
            conn = stomp.Connection([(AMQ_HOST, AMQ_PORT)])
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
