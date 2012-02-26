.. _plugins:

Plugins
#######

Ella tries to keep the core framework **as lightweight as possible**. This has
very good reasons:

* it let's what is required for your app to **your decision**
* it minimizes the **dependencies** of core application
* it makes the development faster, because you can enhance your module while
  not needing to update the rest of the code
  
Because of this philosophy, **plugins** were introduced in version **3.0.0**.

Where to get 'em?
*****************

Currently, there are only plugins that were created by us directly. 3rd party
plugins are hopefully on the way -- it depends more o less on you, Mr. Reader :)

Our plugins can be found in our `GitHub repository <http://github.com/ella>`_. 
Here is a list of some interesting ones:

* `Newman <http://github.com/ella/django-newman>`_ - use admin forged directly
  for Ella needs
* `Tagging <http://github.com/ella/ella-tagging>`_ - provides tagging functionality
* `Comments <http://github.com/ella/ella-comments>`_ - simple threaded comments
* `Galleries <http://github.com/ella/ella-galleries>`_ - create galleries from
  your photos
* `Polls <http://github.com/ella/ella-polls>`_ - let users vote for things and 
  compete
* `Imports <http://github.com/ella/ella-imports>`_ - load stuff from other sites
* `Series <http://github.com/ella/ella-series>`_ - create series from articles 
  covering same topic

Basic plugin structure
**********************

All Ella plugins come as Django applications bundled using setuptools. Each
plugin has dependency on the Ella's core, so Ella is always required and plugins
can hardly be used without it.

As Ella provides significant flexibility, plugins are able to do quite a lot of
magic, like following:

* Define custom ``Publishable`` objects via subclassing. For more details,
  see :ref:`plugins-subclassing-publishable`.
* Extend actions performed over the ``Publishable`` objects, for details,
  see :ref:`plugins-overriding-publishable-urls` section.
* Create custom ``Box`` classess for fine-tuned includes. This is discussed in
  detail in section :ref:`plugins-custom-boxes`.
* Provide additional methods of listing ``Publishable`` objects for a category,
  see :ref:`plugins-listing-handlers`.
* Define related finder functions to get related ``Publishable`` instances, see
  :ref:`plugins-related-finders`.

Plugin API
**********

.. toctree::
    :maxdepth: 2
    :glob:
    
    models
    boxes
    custom_urls
    listing_handlers
    related_finders
