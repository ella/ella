# -*- coding: utf-8 -*-
from django.contrib.auth.models import User, Group, Permission
from django.contrib.sites.models import Site


from djangosanetesting.cases import DatabaseTestCase

from ella.newman.models import CategoryUserRole, DenormalizedCategoryUserRole, has_model_list_permission
from ella.newman.models import has_category_permission, has_object_permission, category_children, compute_applicable_categories
from ella.newman.models import applicable_categories, permission_filtered_model_qs, is_category_fk, model_category_fk_value
from ella.newman.models import model_category_fk
from ella.core.models import Category, Author
from ella.articles.models import Article, ArticleContents
from django.contrib.contenttypes.models import ContentType

def get_permission(code):
    app_label, codename = code.split('.', 1)
    perms = Permission.objects.filter( content_type__app_label=app_label, codename=codename )
    if perms:
        return perms[0]

def recreate_permissions(codenames, role):
    perms = map(lambda p: get_permission(p), codenames)
    map( lambda o: role.group.permissions.remove( o ), role.group.permissions.all() )
    for p in perms:
        role.group.permissions.add(p)
    role.save()

class TestRolePermissions(DatabaseTestCase):

    def setUp(self):
        super(TestRolePermissions, self).setUp()
        #self.create_groups()
        #call_command('syncroles', verbosity=0, notransaction=True)

        self.site = Site.objects.get(name='example.com')
        # superuser
        self.user = User.objects.create(
            username='newman',
            first_name='Paul',
            last_name='Newman',
            email='',
            is_active=True,
            is_staff=True,
            is_superuser=False
        )

        self.create_categories()
        self.create_permissions()
        self.create_groups()
        self.create_roles()

    def create_categories(self):
        site = self.site
        # Category Tree A
        category_top_level = Category.objects.create(slug='a0-top', title='a0 top', description='A top category', site=site)
        self.nested_first_level = Category.objects.create(
            tree_parent=category_top_level,
            slug='a1-first-nested-level',
            title='a1 first nested level',
            description='nested',
            site=site
        )
        self.nested_first_level_two = Category.objects.create(
            tree_parent=category_top_level,
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

    def create_permissions(self):
        self.article_ct = ContentType.objects.get_for_model(Article)
        for i in ['view']:
            setattr(self, "permission_%s_article" % i, Permission.objects.create(content_type=self.article_ct, codename='%s_article' % i, name="Can view aritcle"))

    def create_groups(self):
        self.group = Group.objects.create(name=u'Permission Group')
        for perm in ["view", "change", "delete"]:
            self.group.permissions.add(Permission.objects.get(content_type=self.article_ct, codename="%s_article" % perm))
        self.group.save()

    def create_roles(self):
        self.role = CategoryUserRole(user=self.user)
        self.role.group = self.group
        self.role.save()
        self.role.category.add(self.nested_first_level_two)
        self.role.save()

    def test_denormalized_applicable_categories_same_as_computed_ones(self):
        # test applicable_categories() compare results of  compute_applicable_categories
        computed_categories = compute_applicable_categories(self.user)
        computed_categories.sort()

        denormalized_categories = applicable_categories(self.user)
        denormalized_categories.sort()

        self.assert_equals(computed_categories, denormalized_categories)


    def test_denormalized_applicable_categories_same_as_computed_ones_using_permissions(self):
        computed_categories = compute_applicable_categories(self.user, 'articles.view_article')
        computed_categories.sort()

        denormalized_categories = applicable_categories(self.user, 'articles.view_article')
        denormalized_categories.sort()

        self.assert_equals(computed_categories, denormalized_categories)

