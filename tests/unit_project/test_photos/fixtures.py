from django.conf import settings
from django.contrib.sites.models import Site

from ella.photos.models import Format

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
    