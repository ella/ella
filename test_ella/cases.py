from django.test import TestCase

from ella.core.cache.redis import client

class RedisTestCase(TestCase):
    def tearDown(self):
        super(RedisTestCase, self).tearDown()
        client.flushdb()
