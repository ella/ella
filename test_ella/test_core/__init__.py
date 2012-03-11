# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from django.conf import settings

from ella.core.models import Category, Listing, Publishable
# choose Article as an example publishable
from ella.articles.models import Article

def create_basic_categories(case):
    case.site_id = getattr(settings, "SITE_ID", 1)

    case.category = Category.objects.create(
        title=u"你好 category",
        description=u"exmple testing category",
        site_id=case.site_id,
        slug=u"ni-hao-category",
    )

    case.category_nested = Category.objects.create(
        title=u"nested category",
        description=u"category nested in case.category",
        tree_parent=case.category,
        site_id=case.site_id,
        slug=u"nested-category",
    )

    case.category_nested_second = Category.objects.create(
        title=u" second nested category",
        description=u"category nested in case.category_nested",
        tree_parent=case.category_nested,
        site_id=case.site_id,
        slug=u"second-nested-category",
    )
    case.addCleanup(Category.objects.clear_cache)

def create_and_place_a_publishable(case):
    case.publishable = Article.objects.create(
        title=u'First Article',
        slug=u'first-article',
        description=u'Some\nlonger\ntext',
        category=case.category_nested,
        publish_from=datetime(2008, 1, 10),
        published=True,
        content='Some even longer test. \n' * 5
    )
    case.only_publishable = Publishable.objects.get(pk=case.publishable.pk)

def create_and_place_more_publishables(case):
    """
    Create an article in every category
    """
    case.publishables = []
    for i, c in enumerate(Category.objects.order_by('pk')):

        p = Article.objects.create(
                title=u'Article number %d.' % i,
                slug=u'article-' + chr(ord('a') + i),
                description=u'Some\nlonger\ntext',
                category=c,
                publish_from=datetime(2008, 1, 10),
                published=True,
                content='Some even longer test. \n' * 5
            )
        case.publishables.append(p)

def list_all_publishables_in_category_by_hour(case, category=None):
    case.listings = []

    publish_from = case.publishables[0].publish_from

    for p in case.publishables:
        case.listings.append(
            Listing.objects.create(
                publishable=p,
                category=category or p.category,
                publish_from=publish_from,
            )
        )
        publish_from += timedelta(seconds=3600)
    case.listings.reverse()

def create_and_place_two_publishables_and_listings(case):
    """
    Create two articles and listings
    """

    def place_publishable(model, title, slug, description, category, publish_from, publish_to=None, published=True):
        pu = model.objects.create(
            title=title,
            slug=slug,
            description=description,
            category=category,
            publish_from=publish_from,
            publish_to=publish_to,
            published=published
        )

        li = Listing.objects.create(
            publishable=pu,
            category=c,
            publish_from=pu.publish_from,
            publish_to=publish_to
        )

        case.publishables.append(pu)
        case.listings.append(li)


    c = case.category
    now = datetime.now()

    case.publishables = []
    case.listings = []
    case.hitcounts_all = []
    case.hitcounts_age_limited = []
    case.hitcounts_galleries = []

    publish_from = now - timedelta(days=90)
    publish_to = now - timedelta(days=30)
    place_publishable(
        model=Article,
        title=u'Inactive',
        slug=u'article-inactive',
        description=u'Some\nlonger\ntext',
        category=c,
        publish_from=publish_from.date(),
        publish_to=publish_to.date(),
    )

    publish_from = datetime.now() - timedelta(days=8)

    place_publishable(
        model=Article,
        title=u'Newer',
        slug=u'article-newer',
        description=u'Some\nlonger\ntext',
        category=c,
        publish_from=now.date()
    )

    publish_from = now + timedelta(days=1)
    place_publishable(
        model=Article,
        title=u'Future',
        slug=u'article-future',
        description=u'Some\nlonger\ntext',
        category=c,
        publish_from=publish_from.date()
    )
