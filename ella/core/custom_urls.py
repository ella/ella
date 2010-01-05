import re

from django.http import Http404
from django.conf.urls.defaults import patterns, url, include
from django.core.urlresolvers import RegexURLResolver


ALL = '__ALL__'


class CustomURLResolver(object):
    """
    Our custom url dispatcher that allows for custom actions on objects.

    Usage:
        Register your own view function for some specific URL that is appended to object's absolute url.
        This view will then be called when this URL is used. A small dictionary containing the object,
        it's placement, category, content_type and content_type_name will be passed to the view.

    Example:
        dispatcher.register(urlpatterns, prefix='rate')
        will make the urlpatterns available under /rate/ after any object's URL...
    """
    def __init__(self):
        self._patterns = {}
        self.root_mapping = {}

    def has_custom_detail(self, obj):
        return obj.__class__ in self.root_mapping

    def _get_custom_detail_view(self, model):
        if model not in self.root_mapping:
            raise Http404()
        return self.root_mapping[model]

    def call_custom_detail(self, request, context):
        model = context['object'].__class__
        view = self._get_custom_detail_view(model)
        return view(request, context)

    def register_custom_detail(self, model, view):
        assert model not in self.root_mapping, "You can only register one function for model %r" % model.__name__
        self.root_mapping[model] = view

    def register(self, urlpatterns, prefix=None, model=None):
        key = str(model._meta) if model else ALL
        if prefix:
            urlpatterns = patterns('',
                    url('^%s/' % re.escape(prefix), include((urlpatterns, '', ''))),
                )
        self._patterns.setdefault(key, []).extend(urlpatterns)

    def _get_resolver(self, obj):
        return RegexURLResolver(r'^', self._patterns.get(str(obj._meta), []) + self._patterns.get(ALL, []))

    def resolve(self, obj, url_remainder):
        return self._get_resolver(obj).resolve(url_remainder)

    def reverse(self, obj, view_name, *args, **kwargs):
        return obj.get_absolute_url() + self._get_resolver(obj).reverse(view_name, *args, **kwargs)

    def call_custom_view(self, request, obj, url_remainder, context):
        view, args, kwargs = self.resolve(obj, url_remainder)
        return view(request, context, *args, **kwargs)

resolver = CustomURLResolver()
