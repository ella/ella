from django.http import Http404
from django.template.defaultfilters import slugify


ALL = '__ALL__'


class DetailDispatcher(object):
    """
    Our custom url dispatcher that allows for custom actions on objects.

    Usage:
        Register your own view function for some specific URL that is appended to object's absolute url.
        This view will then be called when this URL is used. A small dictionary containing the object,
        it's placement, category, content_type and content_type_name will be passed to the view.

    Example:
        dispatcher.register('rate', rate_object)
        will make the rate_object view available under /rate/...

        dispatcher.register('vote', poll_vote, polls.Poll)
        will enable you to vote for polls under their own url
    """
    def __init__(self):
        self.custom_mapping = {}
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

    def register(self, start, view, model=None):
        """
        Registers a new custom_mapping to view.

        Params:
            start - first word of the url remainder - the key for the view
            view - the view that acts on this signal
            model - optional, only bind to objects of this model

        Raises:
            AssertionError if the key is already used
        """
        start = slugify(start)
        if start in self.custom_mapping:
            assert not model or model not in self.custom_mapping[start], "You can only register one function for key %r and model %r" % (start, model.__name__)
            assert model is not None or ALL not in self.custom_mapping[start], "You can only register one function for key %r" % start

        map = self.custom_mapping.setdefault(start, {})
        if model:
            map[model] = view
        else:
            map[ALL] = view

    def _get_view(self, start, model):
        """
        Return appropriate view for given bit,
        either from map registered for given model or from __ALL__
        """
        if start not in self.custom_mapping:
            raise Http404

        map = self.custom_mapping[start]
        if model in map:
            view = map[model]
        elif ALL in map:
            view = map[ALL]
        else:
            raise Http404()

        return view

    def call_view(self, request, bits, context):
        """
        Call the custom view.

        Params:
            request - Django's HttpRequest
            bits - url remainder splitted by '/'
            context - a dictionary containing the object,
                      it's placement, category and content_type name

        Raises:
            Http404 if no view is associated with bits[0] for content_type of the object
        """
        model = context['object'].__class__
        view = self._get_view(bits[0], model)
        return view(request, bits[1:], context)

dispatcher = DetailDispatcher()

import re

from django.conf.urls.defaults import patterns, url, include
from django.core.urlresolvers import RegexURLResolver

class CustomURLResolver(object):
    def __init__(self):
        self._patterns = {}

    def register(self, start, urlpatterns, model=None):
        key = str(model._meta) if model else ALL
        self._patterns.setdefault(key, []).extend(patterns('',
                url('^%s/' % re.escape(start), include((urlpatterns, '', ''))),
            ))

    def _get_resolver(self, obj):
        return RegexURLResolver(r'^', self._patterns.get(str(obj._meta), []) + self._patterns.get(ALL, []))

    def resolve(self, obj, url_remainder):
        return self._get_resolver(obj).resolve(url_remainder)

    def reverse(self, obj, view_name, *args, **kwargs):
        return obj.get_absolute_url() + self._get_resolver(obj).reverse(view_name, *args, **kwargs)

resolver = CustomURLResolver()
