# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from django.conf import settings

from ella.core.models import Placement, Category, Listing, Publishable, HitCount
# choose Article as an example publishable
from ella.articles.models import Article
from ella.galleries.models import Gallery

def create_basic_categories(case):
    case.site_id = getattr(settings, "SITE_ID", 1)

    case.category = Category.objects.create(
        title=u"你好 category",
        description=u"exmple testing category",
        site_id = case.site_id,
        slug=u"ni-hao-category",
    )

    case.category_nested = Category.objects.create(
        title=u"nested category",
        description=u"category nested in case.category",
        tree_parent=case.category,
        site_id = case.site_id,
        slug=u"nested-category",
    )

    case.category_nested_second = Category.objects.create(
        title=u" second nested category",
        description=u"category nested in case.category_nested",
        tree_parent=case.category_nested,
        site_id = case.site_id,
        slug=u"second-nested-category",
    )

def create_and_place_a_publishable(case):
    case.publishable = Article.objects.create(
        title=u'First Article',
        slug=u'first-article',
        description=u'Some\nlonger\ntext',
        category=case.category_nested
    )

    case.only_publishable = Publishable.objects.get(pk=case.publishable.pk)

    case.placement = Placement.objects.create(
        publishable=case.publishable,
        category=case.category_nested,
        publish_from=datetime(2008,1,10)
    )

def create_and_place_more_publishables(case):
    """
    Create an article in every category
    """
    case.publishables = []
    case.placements = []

    for i, c in enumerate(Category.objects.order_by('pk')):

        p = Article.objects.create(
                title=u'Article number %d.' % i,
                slug=u'article-' + chr(ord('a')+i),
                description=u'Some\nlonger\ntext',
                category=c
            )
        case.publishables.append(p)

        pl = Placement.objects.create(
                publishable=p,
                category=c,
                publish_from=datetime(2008,1,10)
            )
        case.placements.append(pl)

def list_all_placements_in_category_by_hour(case, category=None):
    case.listings = []

    publish_from = case.placements[0].publish_from

    for p in case.placements:
        case.listings.append(
            Listing.objects.create(
                placement=p,
                category=category or p.category,
                publish_from=publish_from,
            )    
        )
        publish_from += timedelta(seconds=3600)
    case.listings.reverse()

def create_and_place_two_publishables_and_listings(case):
    """
    Create two articles, placements and listings
    """

    def place_publishable(model, title, slug, description, category, publish_from, publish_to=None, hits=1):
        pu = model.objects.create(
            title=title,
            slug=slug,
            description=description,
            category=category
        )

        pl = Placement.objects.create(
            publishable=pu,
            category=c,
            publish_from=publish_from,
            publish_to=publish_to
        )

        HitCount.objects.filter(placement=pl).update(hits=hits)
        hc = HitCount.objects.get(placement=pl)

        li = Listing.objects.create(
            placement=pl,
            category=c,
            publish_from=pl.publish_from,
            publish_to=publish_to
        )

        case.publishables.append(pu)
        case.placements.append(pl)
        case.listings.append(li)

        return hc


    c = case.category
    now = datetime.now()

    case.publishables = []
    case.placements = []
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
        hits=1000
    )

    publish_from = datetime.now() - timedelta(days=8)
    hc = place_publishable(
        model=Gallery,
        title=u'Older',
        slug=u'gallery-older',
        description=u'Some\nlonger\ntext',
        category=c,
        publish_from=publish_from.date(),
        hits=100
    )
    case.hitcounts_all.append(hc)
    case.hitcounts_galleries.append(hc)
    case.hitcount_top = hc

    hc = place_publishable(
        model=Article,
        title=u'Newer',
        slug=u'article-newer',
        description=u'Some\nlonger\ntext',
        category=c,
        publish_from=now.date()
    )
    case.hitcounts_all.append(hc)
    case.hitcounts_age_limited.append(hc)

    publish_from = now + timedelta(days=1)
    place_publishable(
        model=Article,
        title=u'Future',
        slug=u'article-future',
        description=u'Some\nlonger\ntext',
        category=c,
        publish_from=publish_from.date()
    )
