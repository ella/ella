# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from django.conf import settings

from ella.core.models import Placement, Category, Listing, Publishable
# choose Article as an example publishable
from ella.articles.models import Article

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
