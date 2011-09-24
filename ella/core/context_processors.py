from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify
from ella.core.conf import core_settings

current_site = Site.objects.get_current()
current_site_name = slugify(current_site.name)


def url_info(request):
    """
    Make MEDIA_URL and current HttpRequest object
    available in template code.
    """

    return {
        'MEDIA_URL' : core_settings.MEDIA_URL,
        'STATIC_URL': core_settings.STATIC_URL,
        'VERSION' : core_settings.VERSION,
        'SERVER_INFO' : core_settings.SERVER_INFO,
        'SITE_NAME' : current_site_name,
        'CURRENT_SITE': current_site,
    }

def cache(request):

    if not hasattr(request, '_cache_middleware_key'):
        return {}

    return {
        core_settings.ECACHE_INFO: getattr(request, '_cache_middleware_key'),
    }
