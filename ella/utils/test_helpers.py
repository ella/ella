# -*- coding: utf-8 -*-
from datetime import datetime
from tempfile import mkstemp
from PIL import Image
from cStringIO import StringIO

from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.template.defaultfilters import slugify

from ella.core.models import Category, Publishable
# choose Article as an example publishable
from ella.articles.models import Article
from ella.photos.models import Photo

def create_category(title, tree_parent=None, **kwargs):
    defaults = {
        'site_id': getattr(settings, "SITE_ID", 1),
        'slug': slugify(title),
    }
    defaults.update(kwargs)
    if tree_parent is not None:
        tree_parent = Category.objects.get_by_tree_path(tree_parent)
    cat, created = Category.objects.get_or_create(tree_parent=tree_parent, title=title, defaults=defaults)
    return cat

def create_basic_categories(case):
    case.site_id = getattr(settings, "SITE_ID", 1)

    case.category = create_category(u"你好 category",
        description=u"exmple testing category",
        slug=u"ni-hao-category",
    )

    case.category_nested = create_category(
        u"nested category",
        tree_parent='',
        description=u"category nested in case.category",
    )

    case.category_nested_second = create_category(
        u" second nested category",
        tree_parent='nested-category',
        description=u"category nested in case.category_nested",
        slug=u"second-nested-category",
    )
    case.addCleanup(Category.objects.clear_cache)

def create_and_place_a_publishable(case, **kwargs):
    defaults = dict(
        title=u'First Article',
        slug=u'first-article',
        description=u'Some\nlonger\ntext',
        category=case.category_nested,
        publish_from=datetime(2008, 1, 10),
        published=True,
        content='Some even longer test. \n' * 5
    )
    defaults.update(kwargs)
    case.publishable = Article.objects.create(**defaults)
    case.only_publishable = Publishable.objects.get(pk=case.publishable.pk)

def create_photo(case, **kwargs):
    # prepare image in temporary directory
    case.image_file_name = mkstemp(suffix=".jpg", prefix="ella-photo-tests-")[1]
    case.image = Image.new('RGB', (200, 100), "black")
    case.image.save(case.image_file_name, format="jpeg")

    f = open(case.image_file_name)
    file = StringIO(f.read())
    f.close()

    f = InMemoryUploadedFile(
            file = file,
            field_name = 'image',
            name = 'example-photo.jpg',
            content_type = 'image/jpeg',
            size = len(file.getvalue()),
            charset = None
        )

    data = dict(
        title = u"Example 中文 photo",
        slug = u"example-photo",
        height = 200,
        width = 100,
    )
    data.update(kwargs)

    case.photo = Photo(**data)
    image_field = Photo._meta.get_field('image')
    image_field.save_form_data(case.photo, f)

    case.photo.save()
    case.photo._pil_image = case.image

    return case.photo
