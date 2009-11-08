.. _core-views:

==========
Ella views
==========


CategoryDetail
==============

Renders category, also used for site's root (top level category).

**Template names:**

    * ``page/category/<path>/category.html``
    * ``page/category.html``

where:

    * ``<path>`` is the value of category's ``path`` property.

**Template context:**

    * ``category``

ListContentType
===============

Renders archive

**Template names:**
    
    * ``page/category/<path>/content_type/<app>.<model>/listing.html``
    * ``page/category/<path>/listing.html``
    * ``page/content_type/<app>.<model>/listing.html``
    * ``page/listing.html``

where:

    * ``<path>`` is the value of category's ``path`` property.
    * ``<app>`` is the model's ``app_label`` (if filtered by model)
    * ``<model>`` is the model's name (if filtered by model)

**Template context:**
    * ``category``
    * ``listings``: list of ``Listing`` objects ordered by date and priority

    * ``page``: ``django.core.paginator.Page`` instance
    * ``is_paginated``: ``True`` if there are more pages
    * ``results_per_page``: number of objects on one page

    * ``content_type``: ``ContentType`` of the objects, if filtered on content type
    * ``content_type_name``: name of the objects' type, if filtered on content type




ObjectDetail
============

**Template names:**
    
    * ``page/category/<path>/content_type/<app>.<model>/<slug>/object.html``
    * ``page/category/<path>/content_type/<app>.<model>/object.html``
    * ``page/category/<path>/object.html``
    * ``page/content_type/<app>.<model>/object.html``
    * ``page/object.html``

**Template context:**
    * ``placement``: ``Placement`` instance representing the URL accessed
    * ``object``: ``Publishable`` instance bound to the ``placement``
    * ``category``: ``Category`` of the ``placement``
    * ``content_type_name``: slugified plural verbose name of the publishable's content type
    * ``content_type``: ``ContentType`` of the publishable

