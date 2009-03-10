# -*- coding: utf-8 -*-
from datetime import datetime

from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from ella.core.models import Placement, Category
# choose Article as an example publishable, we cannot use Publishable directly
# because it's abstract
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
        perex=u'Some\nlonger\ntext',
        category=case.category_nested
    )

    case.publishable_ct = ContentType.objects.get_for_model(Article)

    case.placement = Placement.objects.create(
        target_ct=case.publishable_ct,
        target_id=case.publishable.pk,
        category=case.category_nested,
        publish_from=datetime(2008,1,10)
    )

def create_and_place_more_publishables(case):
    """
    Create an article in every category
    """
    case.publishable_ct = ContentType.objects.get_for_model(Article)
    case.publishables = []
    case.placements = []

    for i, c in enumerate(Category.objects.all()):

        case.publishables.append(
            Article.objects.create(
                title=u'Article number %d.' % i,
                slug=u'article-' + chr(ord('a')+i),
                perex=u'Some\nlonger\ntext',
                category=c
            )
        )

        case.placements.append(
            Placement.objects.create(
                target_ct=case.publishable_ct,
                target_id=case.publishable.pk,
                category=c,
                publish_from=datetime(2008,1,10)
            )
        )

