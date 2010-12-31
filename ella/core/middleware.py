import time
import re
import logging
log = logging.getLogger('ella.core.middleware')

from django import template
from django.middleware.cache import CacheMiddleware as DjangoCacheMiddleware
from django.core.cache import cache
from django.utils.cache import get_cache_key, add_never_cache_headers, learn_cache_key
from django.conf import settings
from ella.core.conf import core_settings

class DoubleRenderMiddleware(object):

    def _get_excluded_urls(self):
        if hasattr(self, '_excluded_urls'):
            return self._excluded_urls

        if core_settings.DOUBLE_RENDER_EXCLUDE_URLS is None:
            self._excluded_urls = None
            return None

        self._excluded_urls = ()
        for url in core_settings.DOUBLE_RENDER_EXCLUDE_URLS:
            self._excluded_urls += (re.compile(url),)

        return self._excluded_urls

    def process_response(self, request, response):
        if response.status_code != 200 \
            or not response['Content-Type'].startswith('text') \
            or not core_settings.DOUBLE_RENDER:
            return response

        if self._get_excluded_urls() is not None:
            for pattern in self._get_excluded_urls():
                if pattern.match(request.path):
                    return response

        try:
            c = template.RequestContext(request, {'SECOND_RENDER': True})
            t = template.Template(response.content)
            response.content = t.render(c)
            response['Content-Length'] = len(response.content)
        except Exception, e:
            log.warning('Failed to double render on (%s)', unicode(e).encode('utf8'))

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





class UpdateCacheMiddleware(object):
    """
    Response-phase cache middleware that updates the cache if the response is
    cacheable.

    Must be used as part of the two-part update/fetch cache middleware.
    UpdateCacheMiddleware must be the first piece of middleware in
    MIDDLEWARE_CLASSES so that it'll get called last during the response phase.
    """
    def __init__(self):
        self.cache_timeout = settings.CACHE_MIDDLEWARE_SECONDS
        self.key_prefix = settings.CACHE_MIDDLEWARE_KEY_PREFIX
        self.cache_anonymous_only = getattr(settings, 'CACHE_MIDDLEWARE_ANONYMOUS_ONLY', False)

    def process_response(self, request, response):
        """Sets the cache, if needed."""

        # never cache headers + ETag
        add_never_cache_headers(response)

        if not hasattr(request, '_cache_update_cache') or not request._cache_update_cache:
            # We don't need to update the cache, just return.
            return response
        if request.method != 'GET':
            # This is a stronger requirement than above. It is needed
            # because of interactions between this middleware and the
            # HTTPMiddleware, which throws the body of a HEAD-request
            # away before this middleware gets a chance to cache it.
            return response
        if not response.status_code == 200:
            return response

        # use the precomputed cache_key
        if request._cache_middleware_key:
            cache_key = request._cache_middleware_key
        else:
            cache_key = learn_cache_key(request, response, self.cache_timeout, self.key_prefix)

        # include the orig_time information within the cache
        cache.set(cache_key, (time.time(), response), self.cache_timeout)
        return response

class FetchFromCacheMiddleware(object):
    """
    Request-phase cache middleware that fetches a page from the cache.

    Must be used as part of the two-part update/fetch cache middleware.
    FetchFromCacheMiddleware must be the last piece of middleware in
    MIDDLEWARE_CLASSES so that it'll get called last during the request phase.
    """
    def __init__(self):
        self.cache_expire_timeout = settings.CACHE_MIDDLEWARE_SECONDS
        self.key_prefix = settings.CACHE_MIDDLEWARE_KEY_PREFIX
        self.cache_refresh_timeout = getattr(settings, 'CACHE_MIDDLEWARE_REFRESH_SECONDS', self.cache_expire_timeout / 2)
        self.timeout = getattr(settings, 'CACHE_MIDDLEWARE_REFRESH_TIMEOUT', 10)
        self.cache_anonymous_only = getattr(settings, 'CACHE_MIDDLEWARE_ANONYMOUS_ONLY', False)

    def process_request(self, request):
        """
        Checks whether the page is already cached and returns the cached
        version if available.
        """
        if self.cache_anonymous_only:
            assert hasattr(request, 'user'), "The Django cache middleware with CACHE_MIDDLEWARE_ANONYMOUS_ONLY=True requires authentication middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.auth.middleware.AuthenticationMiddleware' before the CacheMiddleware."

        if not request.method in ('GET', 'HEAD') or request.GET:
            request._cache_update_cache = False
            return None # Don't bother checking the cache.

        if self.cache_anonymous_only and request.user.is_authenticated():
            request._cache_update_cache = False
            return None # Don't cache requests from authenticated users.

        cache_key = get_cache_key(request, self.key_prefix)
        request._cache_middleware_key = cache_key

        if cache_key is None:
            request._cache_update_cache = True
            return None # No cache information available, need to rebuild.

        response = cache.get(cache_key, None)
        if response is None:
            request._cache_update_cache = True
            return None # No cache information available, need to rebuild.

        orig_time, response = response
        # time to refresh the cache
        if orig_time and  ((time.time() - orig_time) > self.cache_refresh_timeout):
            request._cache_update_cache = True
            # keep the response in the cache for just self.timeout seconds and mark it for update
            # other requests will continue werving this response from cache while I alone work on refreshing it
            cache.set(cache_key, (None, response), self.timeout)
            return None

        request._cache_update_cache = False
        return response
