from django.core.exceptions import MiddlewareNotUsed
from django.utils.cache import patch_vary_headers

from ella.api.conf import api_settings


class VaryOnAcceptMiddleware(object):
    def __init__(self):
        if not api_settings.ENABLED:
            raise MiddlewareNotUsed()

    def process_response(self, request, response):
        patch_vary_headers(response, ('Accept', ))
        return response
