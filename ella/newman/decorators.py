from django.http import Http404
from django.conf import settings

#def require_AJAX():
#    """
#    Decorator to make a view only accept requests from AJAX calls. Usage::
#        @require_ajax()
#        def my_view(request):
#            # Returns data
#            # ...
#    """
#    def decorator(func):
#        def inner(request, *args, **kwargs):
#            if not request.is_ajax() and not settings.DEBUG:
#                raise Http404, 'Accepts only AJAX call.'
#            return func(request, *args, **kwargs)
#        return inner
#    return decorator

def require_AJAX(func):
    """
    Usage:
       @require_xhr
       def my_view(request):
           pass
    """
    def _decorator(request, *args, **kwargs):
        if request.META.get('HTTP_X_REQUESTED_WITH', "") != 'XMLHttpRequest':
#        if not request.is_ajax() and not settings.DEBUG:
            raise Http404, 'Accepts only AJAX call.'
        return func(request, *args, **kwargs)
    _decorator.__name__ = func.__name__
    _decorator.__doc__ = func.__doc__
    _decorator.__module__ = func.__module__
    return _decorator
