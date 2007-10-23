from django.conf import settings

def url_info(request):
    """
    Make MEDIA_URL and current HttpRequest object
    available in template code.
    """

    VERSION = '$Revision$'
    try:
        VERSION = int(VERSION.split(' ')[1])
    except IndexError:
        VERSION = 1
    except ValueError:
        VERSION = 1

    return {
        'MEDIA_URL' : settings.MEDIA_URL,
        'VERSION' : VERSION,
}

