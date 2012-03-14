# -*- coding: utf-8 -*-
from tempfile import mkstemp
from PIL import Image
from cStringIO import StringIO

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.files.uploadedfile import InMemoryUploadedFile

from ella.photos.models import Format, Photo

__all__ = ("create_photo_formats",)

def create_photo_formats(case):
    case.basic_format = Format(
        name = "basic",
        max_width = 20,
        max_height = 20,
        flexible_height = False,
        stretch = False,
        nocrop = False,
        resample_quality = 85,
    )
    case.basic_format.save()
    case.basic_format.sites.add(Site.objects.get(pk=getattr(settings, "SITE_ID", 1)))
    case.basic_format.save()

# "fixtures" aka example photo
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
