from djangosanetesting.cases import DatabaseTestCase
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from ella.core.models import Author, Category


class NewmanTestCase(DatabaseTestCase):

    def setUp(self):
        super(NewmanTestCase, self).setUp()

        self.site = Site.objects.get(name='example.com')
        self.site_second = Site.objects.create(domain='test.net', name='test.net')

        self.user = User.objects.create(
            username='newman',
            first_name='Paul',
            last_name='Newman',
            email='',
            is_active=True,
            is_staff=True,
            is_superuser=False
        )

        self.author = Author.objects.create(name='igorko', slug='igorko')

        self.create_categories()

    def create_categories(self):
        site = self.site
        # Categories on site 1
        self.category_top_level = Category.objects.create(slug='a0-top', title='a0 top', description='A top category', site=site)
        self.nested_first_level = Category.objects.create(
            tree_parent=self.category_top_level,
            slug='a1-first-nested-level',
            title='a1 first nested level',
            description='nested',
            site=site
        )
        self.nested_first_level_two = Category.objects.create(
            tree_parent=self.category_top_level,
            slug='a2-first-nested-level',
            title='a2 first nested level',
            description='nested',
            site=site
        )
        self.nested_second_level = Category.objects.create(
            tree_parent=self.nested_first_level,
            slug='a4-second-nested-level',
            title='a4 second nested level',
            description='nested',
            site=site
        )
        self.nested_second_level_two = Category.objects.create(
            tree_parent=self.nested_first_level_two,
            slug='a5-second-nested-level',
            title='a5 second nested level',
            description='nested',
            site=site
        )

        # Categories on site 2
        self.category_top_level_b = Category.objects.create(slug='a0-top', title='a0 top', description='A top category', site=self.site_second)
        self.nested_first_level_b = Category.objects.create(
            tree_parent=self.category_top_level_b,
            slug='a1-first-nested-level',
            title='a1 first nested level',
            description='nested',
            site=self.site_second
        )
        self.nested_first_level_two_b = Category.objects.create(
            tree_parent=self.category_top_level_b,
            slug='a2-first-nested-level',
            title='a2 first nested level',
            description='nested',
            site=self.site_second
        )
        self.nested_second_level_b = Category.objects.create(
            tree_parent=self.nested_first_level_b,
            slug='a4-second-nested-level',
            title='a4 second nested level',
            description='nested',
            site=self.site_second
        )
        self.nested_second_level_two_b = Category.objects.create(
            tree_parent=self.nested_first_level_two_b,
            slug='a5-second-nested-level',
            title='a5 second nested level',
            description='nested',
            site=self.site_second
        )

        self.categories = [
            self.category_top_level, self.nested_first_level, self.nested_first_level_two, self.nested_second_level, self.nested_second_level_two,
            self.category_top_level_b, self.nested_first_level_b, self.nested_first_level_two_b, self.nested_second_level_b, self.nested_second_level_two_b,
        ]
