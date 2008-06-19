try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

from django import template
from django.core.cache import cache
from django.middleware.cache import CacheMiddleware
from django.utils.cache import get_cache_key
from django.conf import settings

from ella.core.cache.utils import normalize_key

ECACHE_INFO = 'ella.core.middleware.ECACHE_INFO'

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
        if response.status_code != 200 or not getattr(settings, 'DOUBLE_RENDER', False):
            return response

        c = template.RequestContext(request, {'SECOND_RENDER': True})
        t = template.Template(response.content)
        response.content = t.render(c)
        return response


class CacheMiddleware(CacheMiddleware):
    def process_request(self, request):
        "Checks whether the page is already cached and returns the cached version if available."
        if self.cache_anonymous_only:
            assert hasattr(request, 'user'), "The Django cache middleware with CACHE_MIDDLEWARE_ANONYMOUS_ONLY=True requires authentication middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.auth.middleware.AuthenticationMiddleware' before the CacheMiddleware."

        if not request.method in ('GET', 'HEAD') or request.GET:
            request._cache_update_cache = False
            return None # Don't bother checking the cache.

        if self.cache_anonymous_only and request.user.is_authenticated():
            request._cache_update_cache = False
            return None # Don't cache requests from authenticated users.

        cache_key = get_cache_key(request, self.key_prefix)
        if cache_key is None:
            request._cache_update_cache = True
            return None # No cache information available, need to rebuild.

        cache_key = normalize_key(cache_key)

        response = cache.get(cache_key, None)
        if response is None:
            request._cache_update_cache = True
            return None # No cache information available, need to rebuild.
        request._cache_middleware_key = cache_key
        request._cache_update_cache = False
        return response
