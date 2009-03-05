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
    map( lambda o: role_vca.group_vca.permissions.remove( o ), role_vca.group_vca.permissions.all() )
    for p in perms:
        role_vca.group_vca.permissions.add(p)
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

        self.categories = [self.category_top_level, self.nested_first_level, self.nested_first_level_two, self.nested_second_level, self.nested_second_level_two]

    def create_permissions(self):
        self.article_ct = ContentType.objects.get_for_model(Article)
        for i in ['view']:
            setattr(self, "permission_%s_article" % i, Permission.objects.create(content_type=self.article_ct, codename='%s_article' % i, name="Can view aritcle"))

    def create_groups(self):
        self.group_vca = Group.objects.create(name=u'Permission Group: View, Change, Add')
        for perm in ["view", "change", "add"]:
            self.group_vca.permissions.add(Permission.objects.get(content_type=self.article_ct, codename="%s_article" % perm))
        self.group_vca.save()

        self.group_all = Group.objects.create(name=u'Permission Group: Do Whatever Ya Want')
        for perm in ["view", "change", "add", "delete"]:
            self.group_all.permissions.add(Permission.objects.get(content_type=self.article_ct, codename="%s_article" % perm))
        self.group_all.save()


    def create_roles(self):
        self.role_vca = CategoryUserRole(user=self.user)
        self.role_vca.group = self.group_vca
        self.role_vca.save()
        self.role_vca.category.add(self.nested_first_level_two)
        self.role_vca.save()

        self.role_all = CategoryUserRole(user=self.user)
        self.role_all.group = self.group_all
        self.role_all.save()
        self.role_all.category.add(self.nested_second_level_two)
        self.role_all.save()

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

    def test_applicable_categories_for_user(self):
        categories = applicable_categories(self.user)
        # we expect category from roles + nested ones
        expected_categories = [self.nested_first_level_two.pk, self.nested_second_level_two.pk]

        self.assert_equals(expected_categories, categories)

    def test_applicable_categories_for_user_permission_view(self):
        categories = applicable_categories(self.user, 'articles.view_article')
        # we expect category from roles + nested ones
        expected_categories = [self.nested_first_level_two.pk, self.nested_second_level_two.pk]

        self.assert_equals(expected_categories, categories)

    def test_applicable_categories_for_user_permission_delete(self):
        categories = applicable_categories(self.user, 'articles.delete_article')
        self.assert_equals(self.nested_second_level_two.pk, categories[0])

    def test_has_category_permission_success(self):
        self.assert_true(has_category_permission(self.user, self.nested_second_level_two, 'articles.view_article'))
        self.assert_true(has_category_permission(self.user, self.nested_second_level_two, 'articles.add_article'))
        self.assert_true(has_category_permission(self.user, self.nested_second_level_two, 'articles.change_article'))
        self.assert_true(has_category_permission(self.user, self.nested_second_level_two, 'articles.delete_article'))

    def test_has_category_permission_invalid_permission_name(self):
        self.assert_false(has_category_permission(self.user, self.nested_second_level_two, 'articles.nonexistent'))

    def test_has_category_permission_permission_not_given(self):
        self.assert_false(has_category_permission(self.user, self.nested_first_level_two, 'articles.delete_article'))

    def _create_author_and_article(self):
        author = Author.objects.create(name='igorko', slug='igorko')
        article = Article.objects.create(title=u'Pokusny zajic', perex=u'Perex', category=self.nested_first_level_two)
        ArticleContents.objects.create(title=u'Pokusny zajic, 你好', content=u'Long vehicle', article=article)
        article.authors.add(author)
        article.save()
        self.assert_equals(1, Article.objects.count())

        return article

    def test_has_object_permission_success(self):
        article = self._create_author_and_article()
        # test
        self.assert_true(has_object_permission(self.user, article, 'articles.view_article'))
        self.assert_true(has_object_permission(self.user, article, 'articles.change_article'))
        self.assert_true(has_object_permission(self.user, article, 'articles.add_article'))

    def test_has_object_permission_not_given(self):
        article = self._create_author_and_article()
        self.assert_false(has_object_permission(self.user, article, 'articles.delete_article'))

    def test_has_object_permission_delete_in_forbidden_category(self):
        article = self._create_author_and_article()
        self.assert_false(has_object_permission(self.user, article, 'articles.delete_article'))

#        # delete article in permitted category
#        ar.category = Category.objects.get(slug__startswith='b7')
#        ar.save()
#        self.assert_true( has_object_permission(user, ar, 'articles.delete_article') )
#        # changing, viewing article in forbidden category
#        ar.category = Category.objects.get(slug__startswith='a3')
#        ar.save()
#        self.assert_false( has_object_permission(user, ar, 'articles.change_article') )
