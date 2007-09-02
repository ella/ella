from django.conf import settings

def url_info(request):
    """
    Make MEDIA_URL and current HttpRequest object
    available in template code.
    """

    return {
        'REQUEST' : request,
        'MEDIA_URL' : settings.MEDIA_URL,
}

