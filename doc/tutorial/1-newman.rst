.. _tutorial-1:

=====================
Newman - Ella's admin
=====================

Now when we have a working project from the previous parts of the tutorial, we
need to actually create the site in the admin interface. While we are there we
will also create an article - our very first blog post so that we can actually
have something to work with in our templates in the next step of the tutorial.

.. note::
    If you are impatient to start, just play around with the admin to create
    one instance of ``ella.core.models.Category`` to get the root of the web
    working and then one ``ella.articles.models.Article`` published in that
    category (you might need to create additional model like ``Author`` on the
    way).

First we need some theory on how Ella handles sites, categories and published
objects.


Ella sites and categories
=========================

Ella was designed to server several sites from a single database. It does so by
using Django's built-in `sites framework`_. The ``sites`` app creates a default
``Site`` called ``example.com`` during the syncdb. Just rename the domain name
to relevant value and you will have an ella site, just empty.

Within sites, Ella organizes content into categories. Categories (instances of
``ella.core.models.Category``) are organized in a tree for each site. Every
site needs to have exactly one what we call `root category` - a category
without a parent. This category then represents the root of the web (``/``).

Categories are represented by their ``tree_path`` - a path of ``slugs`` from
root category, for example with categories layout::

    Ella Blog
        About
        Technology
            Concepts
            Django
                Django applications
            Typical deployment env

the ``tree_path`` values would be:

    ======================= ======================================
    Category                tree_path
    ======================= ======================================
    Ella Blog
    About                   about
    Technology              technology
    Concepts                technology/concepts
    Django                  technology/django
    Django applications     technology/django/django-applications
    Typical deployment env  technology/typical-deployment-env
    ======================= ======================================

``Category``'s URL is it's ``tree_path`` (which is what makes the root category
the root of the site) and every post in Ella belongs to one or more categories,
nothing should exist outside of the category tree.

.. _sites framework: http://docs.djangoproject.com/en/dev/ref/contrib/sites/


``Publishable`` and ``Placement``
=================================

Basic function of Ella is publishing content. Ella itself provides several
types of content (``Article``, ``Gallery``, ``Quiz``, ...) and can be easily
extended to add more (just define the model) or used with existing models.

For ease of manipulation and efficiency all content models inherit from
``ella.core.models.Publishable``. This base class has all the fields needed to
display a listing of the content object (``title``, ``description``, ``slug``,
``photo``), basic metadata (``category``, ``authors``, ``source``) and provides
easy access (property ``target``) to the actual instance of the proper class if
needed (it holds a reference to it's ``ContentType``).

By creating a ``Publishable`` object alone, the object is not published - it
has no URL and cannot be accessed from the frontend. To do that we need to
create a ``Placement`` for it.

``Placement`` object represents the actual act of publishing - it defines a URL
and the time for which the published object will be accessible. There are two
types of ``Placement`` with slightly different use cases:

    * *time-based* has URL containing the date of publishing and should be used
      for objects that have some relevance to date (most of the content
      presumably since Ella was designed to power magazines and news sites).
      The URL of an object published by time-based ``Placement`` will look
      like::
        
        /category/tree/path/YEAR/MONTH/DAY/content_type_name/slug/
    
      so for example::
        
        /about/2007/08/11/articles/ella-first-in-production/

    * *static* ``Placement`` has no date in it's URL and should be used for
      objects with universal validity. Since the absence of date limits the
      namespace for such objects we do not recommend using those for large
      amount of objects. URL of static placements contain word 'static' instead
      of the date information::

        /category/tree/path/static/content_type_name/slug/

``content_type_name`` in the URL schema represents slugified translated version
of the model's ``verbose_name_plural``.

Creating a ``Placement`` for some ``Publishable`` object makes it visible
(starting from ``publish_from``) but doesn't make it appear in any listing in
any ``Category``. For that you need to specify in which categories you want it
listed.

.. note::
    
    The distinction between a ``Publishable`` object, it's ``Placement`` and
    ``Listing`` is hidden in the admin interface where everything is presented to
    the user in one form. It is an implementation detail whose understanding helps
    with understanding Ella's capabilities and limitations.
    

``Listing``
===========

``ella.core.models.Listing`` instances carry the information on which
``Placements`` (since an object can have multiple ``Placements`` in multiple
categories on multiple sites, ``Listing`` binds to the ``Placement`` and not to
the object directly) should be listed in which ``Category`` and when - it
enables users to list the object in as many categories as they wish at
arbitrary times (but not sooner that the ``Placement.publish_from``).

By default listings in the root category only contain ``Listings`` specifically
targeted there whereas listings for any subcategory also contains all the
listings of it's subcategories. This is a model we found most useful when
working with large sites where the site's homepage needs to be controlled
closely by editors and the interim categories only serve as aggregators of all
the content published in them either directly or via a subcategory.


Creating a site
===============

Now you should have enough information to be able to start exploring Ella's
admin (found on ``/newman/``) and create your own site and it's first post. You
will know that you were succesful if you manage to create and publish an
article whose URL gives you a ``TemplateDoesNotExist`` exception upon accessing
- that means we are ready to :ref:`create some templates <tutorial-2>` which is the last thing we
need to get our site running.

