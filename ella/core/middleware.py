import logging
log = logging.getLogger('ella.core.middleware')

from django import template
from django.middleware.cache import CacheMiddleware as DjangoCacheMiddleware
from django.utils.cache import get_cache_key, add_never_cache_headers
from django.conf import settings


ECACHE_INFO = 'ella.core.middleware.ECACHE_INFO'

DOUBLE_RENDER = getattr(settings, 'DOUBLE_RENDER', False)

class DoubleRenderMiddleware(object):
    def process_response(self, request, response):
        if response.status_code != 200 or not response['Content-Type'].startswith('text') or not DOUBLE_RENDER:
            return response

        try:
            c = template.RequestContext(request, {'SECOND_RENDER': True})
            t = template.Template(response.content)
            response.content = t.render(c)
        except Exception, e:
            log.warning('Failed to double render on (%s)', e)
        return response

class CacheMiddleware(DjangoCacheMiddleware):
    def process_request(self, request):
        resp = super(CacheMiddleware, self).process_request(request)

        if resp is None:
            request._cache_middleware_key = get_cache_key(request, self.key_prefix)

        return resp

    def process_response(self, request, response):
        resp = super(CacheMiddleware, self).process_response(request, response)

        # never cache headers + ETag
        add_never_cache_headers(resp)

        return resp
