from django.utils import simplejson as json

from ella.api import object_serializer, FULL
from ella.articles.models import Article

from test_ella.test_core.test_views import ViewsTestCase

from nose import tools

class TestCategoryDetail(ViewsTestCase):
    def test_category_is_properly_serialized(self):
        response = self.client.get('/', HTTP_ACCEPT='application/json')
        tools.assert_equals(200, response.status_code)
        tools.assert_equals('application/json', response['Content-Type'])
        tools.assert_equals(
            {
                "category": {"url": "/", "id": 1, "title": u"\u4f60\u597d category"},
                "listings": {
                    u'current_page': 1,
                    u'num_pages': 1,
                    u'objects': [],
                    u'per_page': 20,
                    u'total': 0
                }
            },
            json.loads(response.content)
        )

class TestObjectDetail(ViewsTestCase):
    def setUp(self):
        super(TestObjectDetail, self).setUp()
        self.old_registry = object_serializer._registry.copy()
        object_serializer.register(Article, lambda r, a: 'Article %s' % a.pk, FULL)

    def tearDown(self):
        super(TestObjectDetail, self).tearDown()
        object_serializer._registry = self.old_registry

    def test_article_is_properly_serialized(self):
        response = self.client.get('/nested-category/2008/1/10/first-article/', HTTP_ACCEPT='application/json')
        tools.assert_equals(200, response.status_code)
        tools.assert_equals('application/json', response['Content-Type'])
        tools.assert_equals('Article 1', json.loads(response.content))
