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


