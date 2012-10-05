from django.test import TestCase

from ella.api import object_serializer, FULL
from ella.core.models import Publishable
from ella.articles.models import Article

from nose import tools

class TestObjectSerialization(TestCase):
    def setUp(self):
        super(TestObjectSerialization, self).setUp()
        self.old_registry = object_serializer._registry.copy()
        object_serializer.register(Publishable, lambda r, a: 'Publishable %s' % a.id)

    def tearDown(self):
        super(TestObjectSerialization, self).tearDown()
        object_serializer._registry = self.old_registry

    def test_article_is_properly_serialized(self):
        art = Article(id=42)
        tools.assert_equals('Publishable 42', object_serializer.serialize(None, art, FULL))

