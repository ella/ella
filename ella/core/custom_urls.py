from django.http import Http404
from django.contrib.contenttypes.models import ContentType


class DetailDispatcher(object):
    """
    Our custom url dispatcher that allows for custom actions on objects.
    """
    def __init__(self):
        self.mapping = {}

    def register(self, start, view, content_type=None):
        """
        Registers a new mapping to view.

        Params:
            start - first word of the url remainder - the key for the view
            view - the view that acts on this signal

        Raises:
            AssertionError if the key is already used
        """
        assert start not in self.mapping, "You can only register one function for key %r" % start
        self.mapping[start] = (content_type, view)


    def call_view(self, request, bits, context):
        """
        Call the custom view.

        Params:
            request - Django's HttpRequest
            bits - url remainder splitted by '/'
            context - a dictionary containing the object,
                      it's listing, category and content_type name

        Raises:
            Http404 if no view is associated with bits[0] for content_type of the object
        """
        if bits[0] not in self.mapping:
            raise Http404

        content_type, view = self.mapping[bits[0]]

        if content_type is not None and content_type != ContentType.objects.get_for_model(context['object']):
            raise Http404

        return view(request, bits[1:], context)

dispatcher = DetailDispatcher()
