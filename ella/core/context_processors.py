from django.conf import settings

def url_info(request):
    """
    Make MEDIA_URL and current HttpRequest object
    available in template code.
    """

    return {
        'MEDIA_URL' : settings.MEDIA_URL,
        'VERSION' : getattr(settings, 'VERSION', 1)
}

