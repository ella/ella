.. _tutorial-2:

===============
Basic templates
===============

Now that we have some sample data to work with we can finally start creating
the templates we need to get the site running.

.. note::
    For more information on what templates Ella uses and what context is passed
    in, see :ref:`core-views`.


``page/category.html``
======================

.. highlightlang:: html+django

First we will create a template rendering a category: ``page/category.html``.
This is a default template that will be used for all categories if their
specific template (one with their ``path``) isn't found. The two most important
variables in the context we want to use is ``{{ category }}`` containing the
``Category`` model itself and ``{{ listings }}`` containing a list of
``Listing`` objects for that category ordered by ``publish_from`` and/or
priority.

The basic template will look like::

    <h1>Welcome to category {{ category.title }}</h1>
    <p>{{ category.description }}</p>

    {% for listing in listings %}
        <p>
            <a href="{{ listing.get_absolute_url }}">{{ listing.target.title }}</a>
            {{ listing.target.description|safe }}
        </p>
    {% endfor %}

That will render the category title, description and a list of objects
published in that category. Upon accessing ``/`` you should then see the name
of the category and the article you created in :ref:`previous step
<tutorial-1>`.

.. note::

    ``{{ listing.target }}`` gives you access to the ``Publishable`` instance.
    It gives you an instance of ``Publishable`` even is the object can be a
    subclass, like (in our case) ``Article``. This is done for performance
    reasons, but if you want the access to the actual object in it's proper
    class, you can use ``{{ listing.target.target }}`` at the cost of an
    additional DB query.


``page/listing.html``
=====================

This template represents the archive, it gets the same context as
``page/category.html`` and the same code can be used. We will use the same
code::

    {% extends "page/category.html" %}


``page/object.html``
====================

As with ``page/category.html``, ``page/object.html`` is a fallback template
that will be used for rendering any object if more suitable template isn't
found. In real life we will probably have different templates for different
content types, but to verify the concept and get us started a simple template
should be enough::

    <h1>{{ object.title }}</h1>
    <p>Published on {{ placement.publish_from|date }} in category: <a href="{{ category.get_absolute_url }}">{{ category }}</a></p>
    {{ object.description|safe }}

This template will have access to the actual ``Publishable`` subclass instance
(``Article`` in our case), as opposed to ``page/category.html`` and
``page/listing.html`` which only gets instance of ``Publishable`` by default.


Error pages
===========

By importing ``handler404`` and ``handler500`` in our ``urls.py``, we turned
over the control of error pages to Ella. This means that we need to create two
additional templates: ``page/404.html``::

    <h1>Oops, nothing here</h1>

and ``page/500.html``::

    <h1>If you see this, let us please know how you did it, thanks!</h1>

Now that we have a set of rudimentary templates, we can try :ref:`doing something
useful <tutorial-3>` with them.

