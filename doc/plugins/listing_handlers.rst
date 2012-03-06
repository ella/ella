.. _plugins-listing-handlers:

Listing Handlers
################

By default Ella can list ``Publishable`` in categories using the ``Listing``
model. If additional methods of listing, sorting and pagination is required, a
plugin can define a ``ListingHandler``. For example if makes sense for a
comments plugin to define a ``ListingHandler`` that will allow you to list
``Publishables`` sorted by number of comments.

Project can define multiple ``ListingHandler`` classes and use GET parameters
and optional arguments to the ``{% listing %}`` template tag to determine which
to use on per-request basis.

On top of the default ``ListingHandler``
(``'ella.core.managers.ModelListingHandler'``) Ella also provides an optimized
``RedisListingHandler`` (``'ella.core.cache.redis.RedisListingHandler'``) to be
used on high traffic sites.

Usage
*****

``ListingHandler`` classes a projects is using are defined in settings, a
configuration entry for ``'default'`` must always be present::

    LISTING_HANDLERS = { 
        'default': 'ella.core.managers.ModelListingHandler',
        'comments': 'ella_comments.CommentCountListingHandler',
    }

Interface
*********

``ListingHandler`` is justa class that defines two methods - ``count`` and
``get_listings``::

    from ella.core.managers import ListingHandler

    class CommentsListingHandler(ListingHandler):
        def count(self):
            ...

        def get_listings(self, offset=0, count=10):
            ...

The ``__init__`` method of the class accepts folowing aguments:
category, children=None, content_types=[], date_range=(), exclude=None

.. table:: ``ListingHandler.__init__`` arguments

    ==================== =============  ================================================
    Key                  Default        Value
    ==================== =============  ================================================
    ``category``                        ``Category`` object
    ``children``         ``NONE``       One of ``NONE``, ``IMMEDIATE`` and
                                        ``ALL`` indicating whether to include all 
                                        ``Publishables`` listed in category's
                                        children/descendants. 
    ``content_types``    []             ``ContentType`` instances to filter on.
    ``date_range``       ()             Optional date range to list.
    ``exclude``          None           A ``Publishable`` instance to omit from the
                                        result.
    ==================== =============  ================================================


