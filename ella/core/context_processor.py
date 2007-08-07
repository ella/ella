from django.conf import settings

def url_info(request):
    """
    Return useful variables to know the media url and, if you
    need it, your apps url.
    """

    return {
        'REQUEST' : request,
        'MEDIA_URL' : settings.MEDIA_URL,
}

