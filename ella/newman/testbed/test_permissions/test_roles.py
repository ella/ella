from django.contrib.auth.models import User, AnonymousUser, Permission, Group
from django.core.management import call_command
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.contrib.auth.models import Permission
from django.core import serializers
from django.db import connection, transaction

from djangosanetesting  import cases

from ella.newman.models import CategoryUserRole, DenormalizedCategoryUserRole, has_model_list_permission
from ella.newman.models import has_category_permission, has_object_permission, cat_children, compute_applicable_categories
from ella.newman.models import applicable_categories, permission_filtered_model_qs, is_category_fk, model_category_fk_value
from ella.newman.models import model_category_fk
from ella.core.models import Category, Author
from ella.articles.models import Article, ArticleContents

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

class TestModel(cases.DatabaseTestCase):

    def create_categories(self):
        example = Site.objects.get(name='example.com')
        # Category Tree A
        a0 = Category(slug='a0-top', title='a0 top', description='A top category', site=example)
        a0.save()
        a1 = Category(
            tree_parent=a0,
            slug='a1-first-nested-level', 
            title='a1 first nested level', 
            description='nested', 
            site=example
        )
        a1.save()
        a2 = Category(
            tree_parent=a0,
            slug='a2-first-nested-level', 
            title='a2 first nested level', 
            description='nested', 
            site=example
        )
        a2.save()
        a3 = Category(
            tree_parent=a0,
            slug='a3-first-nested-level', 
            title='a3 first nested level',
            description='nested', 
            site=example
        )
        a3.save()
        a4 = Category(
            tree_parent=a2,
            slug='a4-second-nested-level', 
            title='a4 second nested level',
            description='nested', 
            site=example
        )
        a4.save()
        a5 = Category(
            tree_parent=a2,
            slug='a5-second-nested-level', 
            title='a5 second nested level',
            description='nested', 
            site=example
        )
        a5.save()
        a6 = Category(
            tree_parent=a4,
            slug='a6-third-nested-level', 
            title='a6 third nested level',
            description='nested', 
            site=example
        )
        a6.save()
        # Category Tree B
        thesite = Site(name='b.com', domain='http://b.com')
        thesite.save()
        b0 = Category(slug='b0-top', title='b0 top', description='B top category', site=thesite)
        b0.save()
        b1 = Category(
            tree_parent=b0,
            slug='b1-first-nested-level', 
            title='b1 first nested level', 
            description='nested', 
            site=thesite
        )
        b1.save()
        b2 = Category(
            tree_parent=b0,
            slug='b2-first-nested-level', 
            title='b2 first nested level', 
            description='nested', 
            site=thesite
        )
        b2.save()
        b3 = Category(
            tree_parent=b0,
            slug='b3-first-nested-level', 
            title='b3 first nested level',
            description='nested', 
            site=thesite
        )
        b3.save()
        b4 = Category(
            tree_parent=b3,
            slug='b4-second-nested-level', 
            title='b4 second nested level',
            description='nested', 
            site=thesite
        )
        b4.save()
        b5 = Category(
            tree_parent=b2,
            slug='b5-second-nested-level', 
            title='b5 second nested level',
            description='nested', 
            site=thesite
        )
        b5.save()
        b6 = Category(
            tree_parent=b5,
            slug='b6-third-nested-level', 
            title='b6 third nested level',
            description='nested', 
            site=thesite
        )
        b6.save()
        b7 = Category(
            tree_parent=b5,
            slug='b7-third-nested-level', 
            title='b7 third nested level',
            description='nested', 
            site=thesite
        )
        b7.save()

    def create_groups(self):
        g1 = Group(name='group a')
        g1.save()
        g1.permissions.add( Permission.objects.get(content_type__app_label='articles', codename='view_article') )
        g1.permissions.add( Permission.objects.get(content_type__app_label='articles', codename='change_article') )
        g1.permissions.add( Permission.objects.get(content_type__app_label='articles', codename='view_articlecontents') )
        g1.permissions.add( Permission.objects.get(content_type__app_label='articles', codename='change_articlecontents') )
        g1.permissions.add( Permission.objects.get(content_type__app_label='articles', codename='view_infobox') )
        g1.permissions.add( Permission.objects.get(content_type__app_label='core', codename='view_placement') )
        g1.permissions.add( Permission.objects.get(content_type__app_label='core', codename='view_listing') )
        g1.permissions.add( Permission.objects.get(content_type__app_label='core', codename='change_listing') )
        g1.save()
        # Group B
        g2 = Group(name='group b')
        g2.save()
        g2.permissions.add( Permission.objects.get(content_type__app_label='articles', codename='view_article') )
        g2.permissions.add( Permission.objects.get(content_type__app_label='articles', codename='change_article') )
        g2.permissions.add( Permission.objects.get(content_type__app_label='articles', codename='delete_article') )
        g2.permissions.add( Permission.objects.get(content_type__app_label='articles', codename='view_articlecontents') )
        g2.permissions.add( Permission.objects.get(content_type__app_label='articles', codename='change_articlecontents') )
        g2.permissions.add( Permission.objects.get(content_type__app_label='articles', codename='delete_articlecontents') )
        g2.permissions.add( Permission.objects.get(content_type__app_label='articles', codename='view_infobox') )
        g2.permissions.add( Permission.objects.get(content_type__app_label='core', codename='view_placement') )
        g2.permissions.add( Permission.objects.get(content_type__app_label='core', codename='change_listing') )
        g2.permissions.add( Permission.objects.get(content_type__app_label='core', codename='view_listing') )
        g2.permissions.add( Permission.objects.get(content_type__app_label='core', codename='change_listing') )
        g2.permissions.add( Permission.objects.get(content_type__app_label='core', codename='delete_listing') )
        g2.save()

    def create_users(self):
        u = User(
            username='newman', 
            first_name='Paul',
            last_name='Newman',
            email='',
            is_active=True,
            is_staff=True,
            is_superuser=False
        )
        u.save()

    def create_roles(self):
        role1 = CategoryUserRole(user=User.objects.get(username='newman'))
        role1.group = Group.objects.get(name='group a')
        role1.save()
        role1.category.add(Category.objects.get(slug__startswith='a2'))
        role1.save()
        role2 = CategoryUserRole(user=User.objects.get(username='newman'))
        role2.group = Group.objects.get(name='group b')
        role2.save()
        role2.category.add(Category.objects.get(slug__startswith='b2'))
        role2.save()

    def setUp(self):
        super(TestModel, self).setUp()
        self.create_categories()
        self.create_groups()
        self.create_users()
        self.create_roles()
        #call_command('syncroles', verbosity=0, notransaction=True)

    def test__denormalization(self):
        pass # test applicable_categories() compare results of  compute_applicable_categories 
        user = User.objects.get(username='newman')
        ap_cat = compute_applicable_categories(user)
        ap_cat.sort()
        self.assert_true(ap_cat)
        d_cat = applicable_categories(user)
        d_cat.sort()
        self.assert_true(d_cat)
        self.assert_equals(d_cat, ap_cat)
        # permission specified
        ap_cat = compute_applicable_categories(user, 'articles.view_article')
        ap_cat.sort()
        self.assert_true(ap_cat)
        d_cat = applicable_categories(user, 'articles.view_article')
        d_cat.sort()
        self.assert_true(d_cat)
        self.assert_equals(d_cat, ap_cat)

    def test__applicable_categories__for_user(self):
        user = User.objects.get(username='newman')
        ap_cat = applicable_categories(user)
        ap_cat.sort()
        cats = [3, 5, 6, 7, 10, 13, 14, 15]
        cats.sort()
        self.assert_equals(ap_cat , cats)

    def test__applicable_categories__for_user_permission(self):
        user = User.objects.get(username='newman')
        ap_cat = applicable_categories(user, 'articles.view_article')
        if not ap_cat: self.assert_true(False)
        ap_cat.sort()
        cats = [3, 5, 6, 7, 10, 13, 14, 15]
        cats.sort()
        self.assert_equals( ap_cat , cats )
        # delete privilege
        ap_cat = applicable_categories(user, 'articles.delete_article')
        if not ap_cat: self.assert_true(False)
        ap_cat.sort()
        cats = [10, 13, 14, 15]
        cats.sort()
        self.assert_equals( ap_cat , cats )

    def test__has_category_permission(self):
        user = User.objects.get(username='newman')
        invalid = Category.objects.get(slug__startswith='b1')
        valid = Category.objects.get(slug__startswith='a4')
        self.assert_false( valid is None )
        self.assert_false( invalid is None )
        res = has_category_permission(user, invalid, 'articles.view_article')
        self.assert_false(res)
        res = has_category_permission(user, invalid, 'articles.Xiew_article')
        self.assert_false(res)
        res = has_category_permission(user, invalid, 'photos.view_photo')
        self.assert_false(res)
        res = has_category_permission(user, invalid, 'photos.add_formatedphoto')
        self.assert_false(res)
        res = has_category_permission(user, valid, 'articles.view_article')
        self.assert_true(res)

    def test__has_object_permission(self):
        user = User.objects.get(username='newman')
        # preparing data
        au = Author(name='igorko', slug='igorko')
        au.save()
        ac = ArticleContents(title='Pokusny zajic', content='Long vehicle')
        ar = Article(title='Pokusny zajic', perex='Perex')
        ar.category = Category.objects.get(slug__startswith='a6')
        ar.save()
        ar.authors.add(au)
        ac.article = ar
        ac.save()
        # test
        self.assert_equals(1, Article.objects.count())
        self.assert_true( has_object_permission(user, ar, 'articles.view_article') )
        self.assert_true( has_object_permission(user, ar, 'articles.change_article') )
        # delete article in forbidden category
        self.assert_false( has_object_permission(user, ar, 'articles.delete_article') )
        # delete article in permitted category
        ar.category = Category.objects.get(slug__startswith='b7')
        ar.save()
        self.assert_true( has_object_permission(user, ar, 'articles.delete_article') )
        # changing, viewing article in forbidden category
        ar.category = Category.objects.get(slug__startswith='a3')
        ar.save()
        self.assert_false( has_object_permission(user, ar, 'articles.change_article') )

    def test__permission_filtered_qs(self):
        user = User.objects.get(username='newman')
        # preparing data
        au = Author(name='igorko', slug='igorko')
        au.save()
        # article1
        ac = ArticleContents(title='Pokusny zajic', content='Long vehicle')
        ar1 = Article(title='Pokusny zajic', perex='Perex')
        ar1.category = Category.objects.get(slug__startswith='a6')
        ar1.save()
        ar1.authors.add(au)
        ac.article = ar1
        ac.save()
        # article2
        ac = ArticleContents(title='Zajoch Zwei', content='Cococontent')
        ar2 = Article(title='Pokusny zajic', perex='Perex')
        ar2.category = Category.objects.get(slug__startswith='b1')
        ar2.save()
        ar2.authors.add(au)
        ac.article = ar2
        ac.save()
        # article3
        ac = ArticleContents(title='Zajoch Drei', content='Cococontent')
        ar3 = Article(title='Pokusny zajic', perex='Perex')
        ar3.category = Category.objects.get(slug__startswith='a1')
        ar3.save()
        ar3.authors.add(au)
        ac.article = ar3
        ac.save()
        # test
        filtered_qs = permission_filtered_model_qs( 
            Article.objects.all(), 
            user, 
            ['articles.view_article', 'articles.change_article'] 
        )
        f_data = list(filtered_qs.all())
        valid_data = list( Article.objects.filter(pk=ar1.pk) )
        self.assert_equals(f_data, valid_data)
        # test - delete permission
        filtered_qs = permission_filtered_model_qs( 
            Article.objects.all(), 
            user, 
            ['articles.delete_article', 'core.delete_placement'] 
        )
        f_data = list(filtered_qs.all())
        self.assert_equals(f_data, [])

        ar2.category = Category.objects.get(slug__startswith='b7')
        ar2.save()
        filtered_qs = permission_filtered_model_qs( 
            Article.objects.all(), 
            user, 
            ['articles.delete_article', 'core.delete_placement'] 
        )
        f_data = list(filtered_qs.all())
        valid_data = list( Article.objects.filter(pk=ar2.pk) )
        self.assert_equals(f_data, valid_data)


    def test__is_category_fk(self):
        user = User.objects.get(username='newman')
        # preparing data
        au = Author(name='igorko', slug='igorko')
        au.save()
        ac = ArticleContents(title='Pokusny zajic', content='Long vehicle')
        ar = Article(title='Pokusny zajic', perex='Perex')
        ar.category = Category.objects.get(slug__startswith='a6')
        ar.save()
        ar.authors.add(au)
        ac.article = ar
        ac.save()
        # test
        for f in ar._meta.fields:
            if f.name == 'category':
                self.assert_true(is_category_fk(f))
            elif f.name == 'title':
                self.assert_false(is_category_fk(f))
        self.assert_false(is_category_fk(ar))

    def test__model_category_fk(self):
        self.assert_true(model_category_fk(Article))
        self.assert_false(model_category_fk(ArticleContents))
        from ella.photos.models import Photo
        self.assert_false(model_category_fk(Photo))

    def test__model_category_fk_value(self):
        c = Category.objects.get(slug__startswith='a5')
        self.assert_equals(Category.objects.get(slug__startswith='a2'), model_category_fk_value(c))
        #self.assert_not_equals(Category.objects.get(slug__startswith='a0'), model_category_fk_value(c))
        self.assert_false( Category.objects.get(slug__startswith='a0') == model_category_fk_value(c) )
        c = Category.objects.get(slug__startswith='a3')
        self.assert_equals(Category.objects.get(slug__startswith='a0'), model_category_fk_value(c))
