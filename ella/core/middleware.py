try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

from django import template
from django.conf import settings

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

        c = template.RequestContext(request, {'SECOND_RENDER' : True,})
        t = template.Template(response.content)
        response.content = t.render(c)
        return response

