.. _reference-templatetags:

Templatetags
############

.. highlightlang:: html+django

Core templatetags
*****************

Core templatetags are automatically loaded for your disposal.

.. automodule:: ella.core.templatetags.core
    :members: listing, do_box, do_render, ipblur, emailblur
    
Custom URLs templatetags
************************

.. automodule:: ella.core.templatetags.custom_urls_tags
    :members: custom_url
    
Pagination
**********

When using any of these, you need to call ``{% load pagination %}``
prior to doing it.

.. automodule:: ella.core.templatetags.pagination
    :members: paginator
    
Related
*******

.. automodule:: ella.core.templatetags.related
    :members: do_related
    
Photos
******

.. automodule:: ella.photos.templatetags.photos
    :members: img
    
    
Positions
*********

.. automodule:: ella.positions.templatetags.positions
    :members: position, ifposition