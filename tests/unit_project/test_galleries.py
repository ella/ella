# -*- coding: utf-8 -*-
from datetime import datetime
from djangosanetesting import DatabaseTestCase

from ella.core.models import Placement
from ella.galleries.models import Gallery, GalleryItem

# FIXME hack alert - we are calling the registration here, it should be dealt
# with in the project itself somehow
from ella.galleries import urls

from unit_project.test_core import create_basic_categories
from unit_project import template_loader

def create_and_publish_gallery(case):
    case.publishable = Gallery.objects.create(
        title=u'First Gallery',
        slug=u'first-gallery',
        description=u'Some\nlonger\ntext',
        category=case.category_nested,
        content=u'Some\neven\nlonger\ntext',
    )
    case.publishable2 = Gallery.objects.create(
        title=u'Second Gallery',
        slug=u'second-gallery',
        description=u'Some\nlonger\ntext',
        category=case.category,
        content=u'Some\neven\nlonger\ntext',
    )

    case.placement = Placement.objects.create(
        publishable=case.publishable,
        category=case.category_nested,
        publish_from=datetime(2008,1,10)
    )

    case.galitem = case.publishable.galleryitem_set.create(
        target=case.publishable,
        order=0 
    )

    case.galitem2 = case.publishable.galleryitem_set.create(
        target=case.publishable2,
        order=1 
    )

class TestGalleries(DatabaseTestCase):

    def setUp(self):
        super(TestGalleries, self).setUp()
        create_basic_categories(self)
        create_and_publish_gallery(self)
        template_loader.templates['page/item.html'] = 'page/item.html'

    def tearDown(self):
        super(TestGalleries, self).tearDown()
        template_loader.templates = {}

    def test_gallery_url(self):
        self.assert_equals('/nested-category/2008/1/10/galleries/first-gallery/', self.publishable.get_absolute_url())

    def test_gallery_custom_url_first_item(self):
        self.assert_equals('/nested-category/2008/1/10/galleries/first-gallery/', self.galitem.get_absolute_url())

    def test_gallery_custom_url_item(self):
        self.assert_equals('/nested-category/2008/1/10/galleries/first-gallery/item/second-gallery/', self.galitem2.get_absolute_url())

    def test_two_items_with_same_slug(self):
        galitem3 = self.publishable.galleryitem_set.create(
                target=self.publishable2,
                order=2
            )
        self.assert_equals('second-gallery', self.galitem2.get_slug())
        self.assert_equals('second-gallery1', galitem3.get_slug())
        self.assert_equals('/nested-category/2008/1/10/galleries/first-gallery/item/second-gallery1/', galitem3.get_absolute_url())

    def test_gallery_custom_view_first_item(self):
        response = self.client.get('/nested-category/2008/1/10/galleries/first-gallery/')

        self.assert_true('previous' in response.context)
        self.assert_equals(None, response.context['previous'])

        self.assert_true('next' in response.context)
        self.assert_equals(self.galitem2, response.context['next'])

        self.assert_true('item' in response.context)
        self.assert_equals(self.galitem, response.context['item'])

        self.assert_true('object' in response.context)
        self.assert_equals(self.galitem.target, response.context['object'])

        self.assert_true('position' in response.context)
        self.assert_equals(1, response.context['position'])

        self.assert_true('count' in response.context)
        self.assert_equals(2, response.context['count'])

    def test_gallery_custom_view_item_raises_404_on_non_existent_slug(self):
        template_loader.templates['404.html'] = ''
        response = self.client.get('/nested-category/2008/1/10/galleries/first-gallery/non-existent-slug/')
        self.assert_equals(404, response.status_code)

    def test_gallery_custom_view_item(self):
        response = self.client.get('/nested-category/2008/1/10/galleries/first-gallery/item/second-gallery/')

        self.assert_true('previous' in response.context)
        self.assert_equals(self.galitem, response.context['previous'])

        self.assert_true('next' in response.context)
        self.assert_equals(None, response.context['next'])

        self.assert_true('item' in response.context)
        self.assert_equals(self.galitem2, response.context['item'])

        self.assert_true('object' in response.context)
        self.assert_equals(self.galitem2.target, response.context['object'])

        self.assert_true('position' in response.context)
        self.assert_equals(2, response.context['position'])

        self.assert_true('count' in response.context)
        self.assert_equals(2, response.context['count'])

