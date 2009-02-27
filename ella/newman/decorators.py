from django.http import Http404
from django.conf import settings

def require_AJAX(func):
    def _decorator(obj, request, *args, **kwargs):
        if not request.is_ajax() and not settings.DEBUG:
            raise Http404, 'Accepts only AJAX call.'
        return func(obj, request, *args, **kwargs)
    _decorator.__name__ = func.__name__
    _decorator.__doc__ = func.__doc__
    _decorator.__module__ = func.__module__
    return _decorator
