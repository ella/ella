from django.conf import settings
from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify

current_site = Site.objects.get_current()
current_site_name = slugify(current_site.name)

def url_info(request):
    """
    Make MEDIA_URL and current HttpRequest object
    available in template code.
    """

    return {
        'MEDIA_URL' : settings.MEDIA_URL,
        'VERSION' : getattr(settings, 'VERSION', 1),
        'SITE_NAME' : current_site_name
}

