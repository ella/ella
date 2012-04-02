# -*- coding: utf-8 -*-
from datetime import datetime

from django.conf import settings

from ella.core.models import Category, Publishable
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

