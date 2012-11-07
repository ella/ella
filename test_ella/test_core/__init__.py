# -*- coding: utf-8 -*-
from datetime import timedelta

from ella.core.models import Category, Listing
# choose Article as an example publishable
from ella.articles.models import Article
from ella.utils.test_helpers import create_basic_categories, create_and_place_a_publishable, default_time
from ella.utils import timezone

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
                publish_from=default_time,
                published=True,
                content='Some even longer test. \n' * 5
            )
        case.publishables.append(p)

def list_all_publishables_in_category_by_hour(case, category=None):
    case.listings = []

    publish_from = case.publishables[0].publish_from

    for p in case.publishables:
        case.listings.append(
            Listing.objects.get_or_create(
                publishable=p,
                category=category or p.category,
                publish_from=publish_from,
            )[0]
        )
        publish_from += timedelta(seconds=3600)
    case.listings.reverse()

