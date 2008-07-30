try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

import logging
log = logging.getLogger('ella.core.middleware')

from django import template
from django.core.cache import cache
from django.middleware.cache import CacheMiddleware
from django.utils.cache import get_cache_key, learn_cache_key, add_never_cache_headers
from django.conf import settings

from ella.core.cache.utils import normalize_key


ECACHE_INFO = 'ella.core.middleware.ECACHE_INFO'

DOUBLE_RENDER = getattr(settings, 'DOUBLE_RENDER', False)


_thread_locals = local()
def get_current_request():
    return getattr(_thread_locals, 'request', None)

class ThreadLocalsMiddleware(object):
    """Middleware that gets various objects from the
    request object and saves them in thread local storage."""

    def process_request(self, request):
        _thread_locals.request = request

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


class CacheMiddleware(CacheMiddleware):
    def process_request(self, request):
        resp = super(CacheMiddleware, self).process_request(request)

        if resp is None:
            request._cache_middleware_key = get_cache_key(request, self.key_prefix)

        return resp
