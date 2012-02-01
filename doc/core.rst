.. _design:

Design
######

.. _core-models:

============================
Models - basic design blocks
============================

.. automodule:: ella.core.models.main
    :members: Category, Author, Source

.. _core-templatetags:

============
Templatetags
============

Core templatetags
=================

To use following templatetags, **nothing special is required**. All these tags
are automatically available for your use in templates.

.. automodule:: ella.core.templatetags.core
    :members: do_box, listing, do_render
    
Work with related content
=========================

To use following templatetags, be sure to load them in your Django template 
prior to using them by putting ``{% load related %}`` somewhere at the top of
it.

.. automodule:: ella.core.templatetags.related
    :members: do_related

.. _core-views:    

=====
Views
=====

.. note::

    In any template name ``<tree_path>`` stands for the value of
    ``Category.path``, not it's actual ``tree_path``. This is because of empty
    ``tree_path`` for root categories which would make it impossible to
    override a template for anything in the root category and the root category
    itself.

.. automodule:: ella.core.views
    :members: ListContentType, ObjectDetail

