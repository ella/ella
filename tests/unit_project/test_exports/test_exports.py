# -*- coding: utf-8 -*-
from time import time, localtime, strftime
from datetime import datetime

from djangosanetesting import DatabaseTestCase
from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify

from ella.core.models import Category, Listing, Placement, Author, Publishable
from ella.articles.models import Article
from ella.exports.models import Export, ExportMeta, ExportPosition
from ella.exports.models import UnexportableException

DATE_FORMAT = '%Y-%m-%d %H:%M'
HOUR = 3600
MINUTE = 60

def article_builder(**kwargs):
    title = kwargs.get('title', u'Third Article')
    a = Article.objects.create(
        title=title,
        slug=kwargs.get('slug', slugify(title)),
        description=kwargs.get('description', u'Some\nlonger\ntext'),
        category=kwargs.get('category')
    )
    return Publishable.objects.get(pk=a.pk)

def placement_for_publishable_builder(**kwargs):
    pub = kwargs.get('publishable')
    dat_from = datetime.strptime(kwargs.get('publish_from'), DATE_FORMAT)
    dat_to = datetime.strptime(kwargs.get('publish_to'), DATE_FORMAT)
    return Placement.objects.create(
        publishable=pub,
        category=pub.category,
        slug=pub.slug,
        publish_from=dat_from,
        publish_to=dat_to
    )

def listing_for_placement(**kwargs):
    plac = kwargs.get('placement')
    dat_from = datetime.strptime(kwargs.get('publish_from'), DATE_FORMAT)
    dat_to = datetime.strptime(kwargs.get('publish_to'), DATE_FORMAT)
    out = Listing.objects.create(
        placement=plac,
        category=kwargs.get('category'),
        publish_from=dat_from,
        publish_to=dat_to,
    )
    if 'priority_from' in kwargs and 'priority_to' in kwargs \
        and 'priority_value' in kwargs:
        prio_dat_from = datetime.strptime(kwargs.get('priority_from'), DATE_FORMAT)
        prio_dat_to = datetime.strptime(kwargs.get('priority_to'), DATE_FORMAT)
        out.priority_from = prio_dat_from
        out.priority_to = prio_dat_to
        out.priority_value = kwargs.get('priority_value')

class XTestExport(DatabaseTestCase):
    " Export model and its manager test. "

    def setUp(self):
        super(TestExport, self).setUp()
        self.site = Site.objects.get(name='example.com')
        self.site_second = Site.objects.create(
            domain='test.net', 
            name='test.net'
        )
        self.author = Author.objects.create(name='igorko', slug='igorko')
        # Categories
        self.categoryA = Category.objects.create( 
            title='Category A',
             slug='category-a',
             tree_parent=None,
             description='auauau',
             site=self.site 
        )
        self.categoryB = Category.objects.create( 
            title='Category B',
             slug='category-b',
             tree_parent=self.categoryA,
             description='bububu',
             site=self.site 
        )
        self.categoryH = Category.objects.create( 
            title='Category H',
             slug='category-c',
             tree_parent=self.categoryA,
             description='Export category one.',
             site=self.site 
        )
        self.categoryI = Category.objects.create( 
            title='Category I',
             slug='category-i',
             tree_parent=self.categoryA,
             description='Eksport kategory zwo',
             site=self.site 
        )
        # Publishable objects (Articlez)
        self.publishableA = article_builder(
            title=u'First Article', 
            category=self.categoryA
        )
        self.publishableB = article_builder(
            title=u'Second Article', 
            category=self.categoryA
        )
        self.publishableC = article_builder(
            title=u'Third Article', 
            category=self.categoryA
        )
        self.publishableD = article_builder(
            title=u'Fourth Article', 
            category=self.categoryA
        )
        # Placements, listings & co.
        self.setup_placements_listings()

    def setup_placements_listings(self):
        now = time() + MINUTE
        str_now = strftime(DATE_FORMAT, localtime(now))
        str_future = strftime(DATE_FORMAT, localtime(now + HOUR))

        # publishable A
        self.placementA = placement_for_publishable_builder(
            publishable=self.publishableA,
            publish_from=str_now,
            publish_to=str_future
        )

        str_listingA_from = strftime(DATE_FORMAT, localtime(now + HOUR * 2))
        str_listingA_to = strftime(DATE_FORMAT, localtime(now + HOUR * 3))
        self.listA = listing_for_placement(
            placement=self.placementA,
            publish_from=str_listingA_from,
            publish_to=str_listingA_to,
            category=self.categoryH
        )
        
        # publishable B
        self.placementB = placement_for_publishable_builder(
            publishable=self.publishableB,
            publish_from=str_now,
            publish_to=str_future
        )

        self.listB = listing_for_placement(
            placement=self.placementB,
            publish_from=str_listingA_from,
            publish_to=str_listingA_to,
            category=self.categoryH
        )

        # Exports
        self.exportA = Export.objects.create(
            category=self.categoryH,
            title='hotentot',
            slug='hotentot',
            max_visible_items=2,
        )
        self.exportB = Export.objects.create(
            category=self.categoryI,
            title='export for testing position overrides',
            slug='export-for-testing-position-overrides',
            max_visible_items=3,
        )
        self.export_metaA = ExportMeta.objects.create(
            publishable=self.publishableC,
            title=u'ahoy!',
            description=u'Enjoy polka!',
        )
        ExportPosition.objects.create(
            object=self.export_metaA,
            export=self.exportB,
            visible_from=datetime.strptime(str_now, DATE_FORMAT),
            #visible_to=datetime.strptime(str_listingA_to, DATE_FORMAT),
            position=1
        )
#TODO create test data with only publish_from defined (usual way of creating Listings)

    def test_get_items_for_category(self):
        degen = Export.objects.get_items_for_category(self.categoryH)
        out = map(None, degen)
        self.assert_equals(len(out), 2)
        self.assert_true(self.publishableA in out)
        self.assert_true(self.publishableB in out)

#TODO test get_items_for_category() method to overloaded item position
    def test_get_items_for_category__overloaded_position(self):
        degen = Export.objects.get_items_for_category(self.categoryI)
        out = map(None, degen)
        self.assert_equals(len(out), 2)
        self.assert_true(self.publishableC in out)
        self.assert_true(self.publishableD in out)

#TODO extend test mentioned above to test whether position overloading works right if some of ExportPosition objects have .position == 0.

    def test_get_export_data(self):
        out = Export.objects.get_export_data(
            self.publishableA, 
            export_category=self.categoryH
        )
        right_out = {
            'title': u'First Article',
            'description': u'Some\nlonger\ntext',
            'photo': None
        }
        self.assert_equals(out, right_out)
        # test unexportable publishable (Export object for publishable's category is not present) as well.
        try:
            out = Export.objects.get_export_data(self.publishableD)
            self.assert_equals('Object should not be exportable!', '')
        except UnexportableException:
            pass #OK

    def test_get_export_data__overloading_fields(self):
        out = Export.objects.get_export_data(
            self.publishableC, 
            export_category=self.categoryI
        )
        right_out = {
            'title': u'ahoy!',
            'description': u'Enjoy polka!',
            'photo': None
        }
        self.assert_equals(out, right_out)

    def test_(self):
        pass

# EOF
