.. _plugins-related-finders:

Related finders
###############

To provide maximal flexibility, we use so-called **related finders**. These are
simple functions that are responsible for collecting the related objects. They
are **given name**, so they can be used in templates too (see
:ref:`features-related-templatetag`). The finders are defined
as list of fallback functions and the main controller calls them one by one, 
starting from the top of the list until one of two conditions occur:

#. Required number of related objects have been collected.
#. All finder functions have been called.

The default definition of a related finder is specified this way::

    RELATED_FINDERS = {
        'default': (
            'ella.core.related_finders.directly_related',
            'ella.core.related_finders.related_by_category',
        ),
        'directly': (
            'ella.core.related_finders.directly_related',
        )
    }
    
You can see **two** related finders (namely **default** and **directly**) being
defined as a tuple of functions. You can easily override the default definition
in your ``settings.py`` and add your own related finders to involve advanced
searching (haystack, ...) or your very custom relations. For more info on this
topic, see :ref:`common-gotchas-integrating-search`.

.. warning::

    Be sure to always include the ``default`` key in ``RELATED_FINDERS`` setting,
    it is expected to be there. 

Each finder function follow this signature::

    def related_finder(obj, count, collected_so_far, mods=[], only_from_same_site=True):
        ...
    
==========================  ================================================
Parameter                   Description
==========================  ================================================
``obj``                     Object we are finding the related for.
``count``                   Collect at most this number of related objects.
``collected_so_far``        List of object, that the controller has collected
                            so far. Can come handy when dealing with duplicates.
``only_from_same_site``     Boolean telling the function if only the objects
                            from the same site as ``obj`` is are required.
==========================  ================================================

Each finder is required to return up to the ``count`` of related objects. A valid
option is to return an empty list (``[]``) if no related exist.

Finders are responsible for taking care of duplicates and no duplicates should
be present in intersection of ``collected_so_far`` and what is returned by the
finder function. You can easily use ``if obj not in collected_so_far`` condition
to find duplicates.

