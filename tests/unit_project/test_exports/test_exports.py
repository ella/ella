# -*- coding: utf-8 -*-
from time import time, gmtime, localtime, strftime, sleep
from datetime import datetime, timedelta

from djangosanetesting import DatabaseTestCase
from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify

from ella.core.models import Category, Listing, Placement, Author, Publishable
from ella.articles.models import Article
from ella.photos.models import Format
from ella.ellaexports.models import Export, ExportMeta, ExportPosition
from ella.ellaexports.models import UnexportableException

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
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
    if 'publish_to' in kwargs:
        dat_to = datetime.strptime(kwargs.get('publish_to'), DATE_FORMAT)
    else:
        dat_to = None
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

class TestExport(DatabaseTestCase):
    " Export model and its manager test. "

    def setUp(self):
        super(TestExport, self).setUp()
        #raise self.SkipTest

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
             slug='category-h',
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
        now = datetime.now() - timedelta(seconds=1)
        self.now = now
        self.str_now = now.strftime(DATE_FORMAT)
        future = now + timedelta(hours=1)
        self.str_future = future.strftime(DATE_FORMAT)

        # publishable A
        self.placementA = placement_for_publishable_builder(
            publishable=self.publishableA,
            publish_from=self.str_now,
            publish_to=self.str_future
        )

        self.str_listingA_from = now.strftime(DATE_FORMAT)
        next_three_hours = now + timedelta(hours=3)
        self.str_listingA_to = next_three_hours.strftime(DATE_FORMAT)

        no_future = now - timedelta(hours=2)
        self.str_listingB_from = no_future.strftime(DATE_FORMAT)
        next_hour = now + timedelta(hours=1)
        self.str_listingB_to = next_hour.strftime(DATE_FORMAT)

        prev_hour = now - timedelta(hours=1)
        self.str_listingC_from = prev_hour.strftime(DATE_FORMAT)
        next_two_hours = now + timedelta(hours=2)
        self.str_listingC_to = next_two_hours.strftime(DATE_FORMAT)

        listing_d = now - timedelta(hours=3)
        self.str_listingD_from = listing_d.strftime(DATE_FORMAT)

        self.listA = listing_for_placement(
            placement=self.placementA,
            publish_from=self.str_listingA_from,
            publish_to=self.str_listingA_to,
            category=self.categoryH
        )
        
        # publishable B
        self.placementB = placement_for_publishable_builder(
            publishable=self.publishableB,
            publish_from=self.str_now,
            publish_to=self.str_future
        )

        self.listB = listing_for_placement(
            placement=self.placementB,
            publish_from=self.str_listingB_from,
            publish_to=self.str_listingB_to,
            category=self.categoryH
        )

        # Exports
        self.photo_format = Format.objects.create(
            name='cucorietka',
            max_width=80,
            max_height=66,
            flexible_height=False,
            stretch=False,
            nocrop=True,
        )
        self.photo_format.sites.add(self.site)
        self.photo_format.save()
        self.exportA = Export.objects.create(
            category=self.categoryH,
            use_objects_in_category=True,
            title='hotentot',
            slug='hotentot',
            max_visible_items=2,
            photo_format=self.photo_format
        )
        self.export_position_overrides = Export.objects.create(
            category=self.categoryI,
            use_objects_in_category=True,
            title='export for testing position overrides',
            slug='export-for-testing-position-overrides',
            max_visible_items=3,
            photo_format=self.photo_format
        )
        self.export_metaA = ExportMeta.objects.create(
            publishable=self.publishableC,
            title=u'ahoy!',
            description=u'Enjoy polka!',
        )
        self.export_metaB = ExportMeta.objects.create(
            publishable=self.publishableD,
            title=u'',
            description=u'',
        )
        ExportPosition.objects.create(
            object=self.export_metaA,
            export=self.export_position_overrides,
            visible_from=datetime.strptime(self.str_listingA_from, DATE_FORMAT),
            visible_to=datetime.strptime(self.str_listingA_to, DATE_FORMAT),
            position=2
        )
        ExportPosition.objects.create(
            object=self.export_metaB,
            export=self.export_position_overrides,
            visible_from=datetime.strptime(self.str_listingB_from, DATE_FORMAT),
            visible_to=datetime.strptime(self.str_listingB_to, DATE_FORMAT),
            position=1
        )
#TODO create test data with only publish_from defined (usual way of creating Listings)

    def test_get_items_for_category(self):
        " basic test getting items for certain export category. "
        degen = Export.objects.get_items_for_category(self.categoryH)
        out = map(None, degen)
        self.assert_equals(2 , len(out))
        self.assert_true(self.publishableA.target in out)
        self.assert_true(self.publishableB.target in out)
        # ordering test
        self.assert_equals(
            out,
            [self.publishableA.target, self.publishableB.target]
        )

    def test_get_items_for_category__placed_by_position(self):
        " test get_items_for_category() method to overloaded item position "
        degen = Export.objects.get_items_for_category(self.categoryI)
        out = map(None, degen)
        self.assert_equals(2, len(out))
        self.assert_true(self.publishableC.target in out)
        self.assert_true(self.publishableD.target in out)

    def test_get_items_for_category__placed_by_position_and_by_listings(self):
        """
        test whether position overloading works right if some of ExportPosition 
        objects have .position == 0. 
        """
        listing_for_placement(
            placement=self.placementB,
            publish_from=self.str_listingB_from,
            publish_to=self.str_listingB_to,
            category=self.categoryI
        )
        listing_for_placement(
            placement=self.placementA,
            publish_from=self.str_listingA_from,
            publish_to=self.str_listingA_to,
            category=self.categoryI
        )
        degen = Export.objects.get_items_for_category(self.categoryI)
        out = map(None, degen)
        self.assert_equals(3, len(out))
        self.assert_true(self.publishableC.target in out)
        self.assert_true(self.publishableD.target in out)
        self.assert_true(self.publishableA.target in out)
        self.assert_true(self.publishableB.target not in out)
        # ordering test
        self.assert_equals(
            out, 
            [self.publishableD.target, self.publishableA.target, self.publishableC.target]
        )

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
            'photo': None,
            #'visible_from': datetime(2010, 1, 18, 14, 59)
        }
        del out['visible_from']
        self.assert_equals(out, right_out)

    def test_unique(self):
        "test uniqness of items returned from get_items_for_category() method."
        listing_for_placement(
            placement=self.placementA,
            publish_from=self.str_listingC_from,
            publish_to=self.str_listingC_to,
            category=self.categoryH
        )
        self.exportA.max_visible_items = 5
        self.exportA.save()
        degen = Export.objects.get_items_for_category(self.categoryH)
        out = map(None, degen)
        self.assert_equals(2, len(out))

    def test_unique_positions(self):
        self.export_metaC = ExportMeta.objects.create(
            publishable=self.publishableA,
            title=u'',
            description=u'',
        )
        ExportPosition.objects.create(
            object=self.export_metaC,
            export=self.exportA,
            visible_from=datetime.strptime(self.str_listingB_from, DATE_FORMAT),
            visible_to=datetime.strptime(self.str_listingB_to, DATE_FORMAT),
            position=1
        )
        self.exportA.max_visible_items = 5
        self.exportA.save()
        degen = Export.objects.get_items_for_category(self.categoryH)
        out = map(None, degen)
        self.assert_equals(2, len(out))

    def test_overloaded_item_position(self):
        """ 
        Test whether item placed in export via standard category listing
        is overloaded (including its position) and placed to the right position.
        """
        self.exportB = Export.objects.create(
            category=self.categoryA,
            use_objects_in_category=True,
            title='blb',
            slug='blb',
            max_visible_items=4,
            photo_format=self.photo_format
        )
        # create listings,placements
        self.placement_for_publishableC = placement_for_publishable_builder(
            publishable=self.publishableC,
            publish_from=self.str_now,
            publish_to=self.str_future
        )
        self.placement_for_publishableD = placement_for_publishable_builder(
            publishable=self.publishableD,
            publish_from=self.str_now,
            publish_to=self.str_future
        )

        self.listing_for_publishableA = listing_for_placement(
            placement=self.placementA,
            publish_from=self.str_listingA_from,
            category=self.categoryA
        )
        self.listing_for_publishableB = listing_for_placement(
            placement=self.placementB,
            publish_from=self.str_listingB_from,
            category=self.categoryA
        )
        self.listing_for_publishableC = listing_for_placement(
            placement=self.placement_for_publishableC,
            publish_from=self.str_listingC_from,
            category=self.categoryA
        )
        self.listing_for_publishableD = listing_for_placement(
            placement=self.placement_for_publishableD,
            publish_from=self.str_listingD_from,
            category=self.categoryA
        )

        # Override position and time
        self.export_meta_for_publishableB = ExportMeta.objects.create(
            publishable=self.publishableB,
            title=u'Second article on first position?',
            description=u'',
        )
        b_from = self.now - timedelta(hours=2)
        b_to = self.now + timedelta(hours=1)
        ExportPosition.objects.create(
            object=self.export_meta_for_publishableB,
            export=self.exportB,
            visible_from=b_from,
            visible_to=b_to,
            position=1
        )

        # test exported items
        # FIXME
        """
        [<Publishable: Second article on first position?>, <Publishable: First Article>, <Publishable: ahoy!>, <Publishable: Second article on first position?>]
        """
        items = Export.objects.get_items_for_slug('blb')
        out = map(None, items)
        #print out
        self.assert_equals(4, len(out))
        self.assert_equals(self.publishableB.target, out[0])
        self.assert_equals(self.publishableA.target, out[1])
        self.assert_equals(self.publishableC.target, out[2])
        self.assert_equals(self.publishableD.target, out[3])

    def test_(self):
        " copy/paste template "
        pass

# EOF
