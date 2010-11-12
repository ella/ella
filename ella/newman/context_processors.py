from django.conf import settings
from ella.newman.conf import newman_settings

def newman_media(request):
    """
    Inject NEWMAN_MEDIA_URL to template. Use NEWMAN_MEDIA_PREFIX value from
    settings, if not available, use MEDIA_URL + 'newman_media/' combination
    """
    return {
        'NEWMAN_MEDIA_URL' : newman_settings.MEDIA_PREFIX,
        'DJANGO_MEDIA_URL': getattr(settings, 'MEDIA_URL', ''),
        'DEBUG': settings.DEBUG
    }
