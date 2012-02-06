.. _features:

Features
########

.. _features-template-overview:

Template overview
*****************

Basic templates
===============

Advanced templates
==================

.. _features-template-fallback-mechanisms:

Fallback mechanisms
===================

.. _features-category-detail:

Category detail page
********************

Category detail is the very main page of most content websites. In Ella, we do
not make any difference for homepages and other categories except for the 
different URLs. Ella uses categories in several ways:

* For showing your homepage
* For listing content that is published in the category
* As a static page, e.g. for your contact page

Last use case scenario might be little awkward, but the design decision was 
made to make this as easy as possible. Because main focus of Ella is content-rich
websites and online news, static pages are usually not the primary focus of an 
Ella project. It's still quite simple to create personal websites though.

Working with category templates
===============================

When creating category templates, here are some basic rules you can count on:

The template used is by default ``category.html`` using the template fallback
mechanism (for details on that, see :ref:`features-template-fallback-mechanisms`).
You can set the different template for your category **using administration**.
For details and explanation of the whole concept, have a look at
:ref:`features-category-custom-templates`.

**Context** will always contain at least:

==================================  ================================================
Key                                 Value
==================================  ================================================
``category``                        ``Category`` object itself.
``is_homepage``                     Flag telling you if this is a homepage, see
                                    :ref:`features-category-homepages`.
``is_title_page``                   Boolean telling you if this is the first
                                    page of the listing/archive.
``is_paginated``                    Boolean which is ``True`` more pages are available.
``results_per_page``                Number of objects per page.
``page``                            Current page shown.
``listings``                        Objects listed in the ``category`` for this page.
``content_type``                    If filtering by Content Type is active,
                                    this will hold the ``ContentType`` instance.
``content_type_name``               Verbose name of content type if Content Type
                                    filtering takes place.
==================================  ================================================

The basic scenario when building up site's category templates is following:

#. Create the base template ``page/category.html``. Make this template as generic
   as possible to enable nice
   :ref:`inheritance <common-gotchas-taking-advantage-of-inheritance>`. Most 
   often, this category will be created as generic, paginated, content listing
   as seen on most sites using articles.
#. Create customized template for homepage since it has different layout in 
   most cases. Use proper :ref:`fallback <features-template-fallback-mechanisms>` to tell
   Ella that it should use a different template for HP. It's as simple as 
   putting the template to ``page/category/[YOUR_HP_SLUG]/category.html``. 
   Also, practice inheritance, make this template using
   ``{% extend "page/category.html" %}``.
#. Create other category templates that need customization. You will most likely
   end up building some :ref:`static pages <common-gotchas-static-pages>`.

.. _features-category-homepages:

Homepages
=========

In Ella, a homepage is recognized as the category, that has **no parent**. Therefore,
it is also the **root category**. **Only one** such page is allowed for *each site
that is contained in database*.

The **URL** of homepage is always **"/"**, so for a domain *example.com*, full
URL of root category would be of course the root of the whole site::

    http://www.example.com/

When working with category templates, homepage will set the variable ``is_homepage``
in the template's context to ``True``. Thanks to it, something like this is possible:

.. code-block:: html+django

     <!-- in page/category.html -->
     {% if is_homepage %}
        This is homepage category.
     {% else %}
        This is not a homepage. 
     {% endif %}
     
This makes it very easy to have only one template which covers most of the
category pages including homepage. However, you should always consider splitting
the HP-specific code to it's own template when the HP layout is *completely 
different* from other categories. This would make your templates much more
readable which is always a good thing.   

Other categories
================

In most Ella sites, categories other than HP usually serve for **content listings**
or :ref:`static pages <common-gotchas-static-pages>`. We'll demonstrate the 
basic code for content listing for the sake of completness.

.. code-block:: html+django

    {% extends "page/base.html" %}
    
    {% block content %}
        {% block object_listing %}
            {% listing 10 for category as category_listing %}
            {% for l in category_listing %}
                {% box listing for l.target %}{% endbox %}
            {% endfor %}
        {% endblock %}
        {% block pagination %}
           {% if is_paginated %}{% paginator 5 %}{% endif %}
        {% endblock %}
    {% endblock %}  

.. _features-category-custom-templates:

Defining custom template for category
=====================================

By default, template used for rendering category is ``category.html``. You 
can override this behavior to use your custom template. This can be useful
when you need to implement several different layouts for your categories.
Suppose we have following layouts:

* Top 4 articles, then listing of 6 more
* Listing of 10 articles without top ones
* Listing of 10 articles without perexes, only big images

If it wasn't possible to select a template for category, you would need to 
override the template for each category diferrent from the base one (let it be
the first one). Using different templates, you can avoid doing so. First, define
the templates in your ``settings.py``::

    # in settings.py
    CATEGORY_TEMPLATES = (
        ('category.html', 'default (top 4 + listing 6)'),
        ('category_10.html', 'top 10'),
        ('category_10_no_perex.html', 'top 10 w/o perexes'),
    )
    
Next, create the **base template**. That would be ``category.html``. It would 
be used, when not set otherwise in your Ella administration:

.. code-block:: html+django

    <!-- in page/category.html -->
    {% extends "page/base.html" %}
    
    {% block object_listing %}
        <!-- show 4 boxes with big images -->
        {% listing 4 for category as category_listing %}
        {% for l in category_listing %}
            {% box listing_big_image for l.target %}{% endbox %}
        {% endfor %}
        
        <!-- show 6 more regular boxes -->
        {% listing 6 from 4 for category as category_listing %}
        {% for l in category_listing %}
            {% box listing for l.target %}{% endbox %}
        {% endfor %}
    {% endblock %}
    
Then, you would create ``category_10.html`` template to show only ten same boxes
for listing:
    
.. code-block:: html+django

    <!-- in page/category_10.html -->
    {% extends "page/category.html" %}
    
    {% block object_listing %}
        <!-- show 10 same boxes -->
        {% listing 10 for category as category_listing %}
        {% for l in category_listing %}
            {% box listing for l.target %}{% endbox %}
        {% endfor %}
    {% endblock %}
    
Finally, create the last ``category_10_no_perex.html`` template, that would
define the last layout: 
    
.. code-block:: html+django
    
    <!-- in page/category_10_no_perex.html -->
    {% extends "page/category.html" %}
    
    {% block object_listing %}
        <!-- show 10 boxes without perexes -->
        {% listing 10 for category as category_listing %}
        {% for l in category_listing %}
            {% box listing_no_perex for l.target %}{% endbox %}
        {% endfor %}
    {% endblock %}

This way, you don't need to override template for each of different categories, you
just set the layout in your administration. Also, this is widely used when 
it comes to creating :ref:`common-gotchas-static-pages`.

.. _features-object-detail:

Object detail page
******************

The *object detail* in Ella terminology is a detail of a publishable object. 
This can be the **article itself**, a **page showing gallery** or a page 
with a **video player** we used as example in :ref:`plugins` section. This would
be a main interest for your users, the main source of information on your site.

Similarly to categories, object details use ``object.html`` template. Same 
fallback rules apply (see :ref:`features-template-fallback-mechanisms`).

When dealing with object detail, you can be sure the context will provide you
with following data:

==================================  ================================================
Key                                 Value
==================================  ================================================
``object``                          ``Publishable`` subclass instance we are
                                    dealing with.
``category``                        Related ``Category`` object for this page.
``content_type``                    ``ContentType`` instance of the ``object``.
``content_type_name``               Verbose name of content type if Content Type.
==================================  ================================================

Defining templates follows a same pattern as when working with categories:

#. Define a **generic template that** will be used when rendering objects without
   some special behavior. In this template, try to use only attributes defined
   by ``Publishable`` model, so it will work for all subclasses correctly.
#. Define custom templates for **objects of different kinds**. There would mostly
   likely be different templates for **articles**, **galleries** etc. These 
   templates go to ``page/content_type/[APP_LABEL].[MODEL_NAME]/object.html``,
   e.g. ``page/content_type/articles.article/object.html``.
#. Define templates for **custom layout of object in specific categories**. These
   might be sometimes required. Imagine a situation when you need an article
   detail to look differently in some special category. For example, you can
   have normal articles and site news, both of which are internally implemented
   as ``Article`` instances. It makes sense for site news to keep a little 
   different layout than normal articles do, you probably won't show the 
   news source and so on.
   
To provide some real world example of basic object page, have a look at this 
small snippet:

.. code-block:: html+django

    <!-- in page/object.html -->
    {% extends "page/base.html" %}
    
    {% block content %}
        <!-- show photo if available -->
        {% if object.photo %}
            {% box object_main for object.photo %}{% endbox %}
        {% endif %}
        
        <!-- show basic information, title, authors, publication date -->
        <h1>{% block object_title %}{{ object }}{% endblock %}</h1>
        
        <p>Published at: <span>{{ object.publish_from|date }}</span></p>
        {% if object.authors.exists %}
            <p>Authors: <strong>{{ object.authors.all|join:", " }}</strong></p>
        {% endif %}
        
        <!-- render perex/description -->
        {% block perex %}
            {% render object.description %}
        {% endblock %}
        
        <!-- body for publishable subclasses goes here -->
        {% block body %}{% endblock %}
        
        <!-- show related objects -->
        {% block related %}
            {% related 5 for object as related %}
            {% for r in related %}
                {% box related for r %}{% endbox %}
            {% endfor %}
        {% endblock %}
    {% endblock %}

Most likely, you would also add following things to the base object template:

* Facebook like button, Twitter tweet button, Google +1 button
* Sharing handlers - send by email, ...
* Tags for the object
* Comments

.. _features-category-archives:

Archive pages
*************

.. _features-custom-views:

Integrating custom views
************************

.. _features-positions:

Defining positions on the page
******************************

Position is understood as placeholder on the page whose context is specific
to the category in use. It allows designers to specify areas of the template to
be overriden by the site writers, editors via the admin interface. Position is
identified by it's name. Main use case of positions is box embedding, but raw
HTML can be used as well.

**inheritance**
    When called from the template tag, the application will first try and
    locate the active position for the given category, then, if such position
    is not available, it will locate active position in the closest ancestor of
    the category. This behavior can be overriden by the ``nofallback`` argument to
    the ``{% position %}`` templatetag.

**tied to objects or raw HTML**
    You can either define a generic foreign key to any object whose box you
    wish to display instead of the templatetag or, if the generic foreign key
    is empty, raw HTML that you wish to insert.

``{% ifposition %}`` **templatetag**
    You can check if any position for a given set of names is active using the
    ``{% ifposition %}`` templatetag. It behaves in same way as common ``{% if %}``
    templatetag.

Using positions in your pages
=============================

Position is defined in the admin interface and used from the templates via two
templatetags.

``{% position %}`` template tag
-------------------------------

Render a given position for category.

Syntax:

.. code-block:: html+django

    {% position POSITION_NAME for CATEGORY [using BOX_TYPE] [nofallback] %}
      ...
    {% endposition %}

Parameters:

==========================  ================================================
Name                        Description
==========================  ================================================
``POSITION_NAME``           Name of the position for lookup.
``CATEGORY``                The category for which to render the position - 
                            either a ``Category`` instance or category's
                            ``slug``.
``BOX_TYPE``                Default type of the box to use, can be overriden 
                            from the admin.
``nofallback``              If present, do not fall back to parent categories.
==========================  ================================================

Text inside the tag (between ``{% position %}`` and ``{% endposition %}``) is
passed to ``Box`` used for rendering the object. This can also be overriden
from the database.
    
``{% ifposition %}`` template tag
---------------------------------

Render template according to the availability of given position names within
given category.

Syntax:

.. code-block:: html+django

    {% ifposition POSITION_NAME ... for CATEGORY [nofallback] %}
        POSITION EXISTS!
    {% else %}
        NO POSITION DEFINED!
    {% endifposition %}

Renders 'POSITION EXISTS!' if any of the space separated position name is active for the
given category, 'NO POSITION DEFINED!' otherwise.

Real world examples
-------------------

Positions are widely used for a lot of page parts that need to be edited by
site staff from time to time, like:

* Site menus (see :ref:`common-gotchas-creating-site-menus`)
* Page sidebars (see :ref:`common-gotchas-sidebars`)
* Top articles on the hompage, which are under strict supervision of editors who
  need to control what exactly and in which order is being displayed.
* Carousel-like content on the bottom of the pages.

.. code-block:: html+django

    <!-- in page/category.html -->
    {% load positions %}
    ...
    
    {% block right_column %}
        {% position rightcol_poll for category %}{% endposition %}
    {% endblock %}
    
    ...

This simple example can be used to show a **poll** in the page right column
in case the poll is defined. It will also switch the poll for the categories
where the specific one is defined as stated before. 

.. _features-photos:

Working with photos
*******************

Ella's core has an integrated photo module which is tightly coupled with the
rest of the modules (articles, ...) and plugins, notably the **Newman
administration plugin**. 

**Features**:

* Photo format definition with cross-site option.
* Scaling, cropping.
* Definition of important box for automatic cropping while keeping the 
  important area on the photo intact (e.g.: keeping faces on cropped photo).
* ``{% img %}`` template tag for template usage.

Photo module is composed from several important parts:

``Photo`` **model**
    Photo model stands for the actual photo uploaded by user.
    
``Format`` **model**
    Describes different formats that a sites is using. Think of format as a
    set of rules how to render: "a big photo aligned to right side", "small 
    photo to show authors face" and so on.

``FormatedPhoto`` **model**
    This model keeps track of photos that have already been formatted in a 
    given format. It works like a cache so that the formatting only occurs 
    once.
    
``{% img %}`` **template tag**
    ``{% img %}`` is used when placing the photos in the templates. It simplifies
    and abstracts the process of thumbnail creation.  


.. _features-photos-photo:

The ``Photo`` model
===================

A ``Photo`` class represents original photo uploaded by user. It keeps all the
meta information:

* ``title``, ``description``, ``slug``
* ``image`` - this is the path to a `Django file storage`_.
* ``width`` and ``height``
* ``important_*`` describes important box on the ``Photo``. This is used when
  cropping images and marks area which should not be cropped in any circumstances.
* ``authors`` - lists photo authors
* ``source`` - a related ``Source`` instance

The original photo is always kept and never altered. All formatting occurs on 
``FormatedPhoto`` instances, which are also kept to keep track of already-formated
photos.

.. _Django file storage: https://docs.djangoproject.com/en/dev/ref/files/storage/ 

.. _features-photos-formats:

Photo formats
=============

For easier administration, Ella uses set of user-defined formats to render the
photos. Format defines following attributes:

* ``name`` is used mainly in templates when referencing a format to use for
  rendering.
* ``max_width`` and ``max_height``
* ``flexible_height`` determines whether ``max_height`` is an absolute maximum, or
    the formatted photo can vary from ``max_height`` for ``flexible_max_height``.
* ``flexible_max_height``
* ``stretch`` describes if photo can be stretched if necessary.
* ``nocrop`` if set to ``True``, no cropping will occur for this format.
* ``resample_quality`` defines quality used for operations over the photo
  (default is 85).
* ``sites`` is list of Ella sites, where the format should be available for use. 


``{% img %}`` template tag
==========================

The ``{% img %}`` template tag is used to get a thumbnail for original ``Photo``
object. It is smart enough to use all the meta info defined on ``Photo``, so 
the **important box** is taken into account.

**Syntax**:

.. code-block:: html+django
        
    {% img <FORMAT> for <VAR> as <VAR_NAME> %}
    {% img <FORMAT> with <FIELD_VALUE> as <VAR_NAME> %} 
    
Templatetag supports two approaches. First is very simple, you just give it
a ``Photo`` instance and it will generate thumbnail for it. The second one
tries to find a ``Photo`` you describe by ``FIELD_VALUE``. See the examples:

.. code-block:: html+django
    
    {% img category_listing for object.photo as thumb %}
    {% img category_listing with pk 1150 as thumb %}

The result (stored as ``thumb`` in the example above) then contains a
``FormatedPhoto`` instance. This means you can access it's attributes,
particularly ``url`` method and ``with`` and ``height``.

.. _features-photo-workflow:

Workflow
========

The basic workflow when using photos goes like this:

#. **Define formats**. This step is usually already done when you enter the 
   stage as the designer is reponsible for it in most cases. We only need to 
   enter the data to the Ella database.
#. **Store the formats in fixtures** is quite important step, because it makes
   development much easier when a more than one developer is involved. It 
   makes sense to add the fixture as `initial data`_ because it shouldn't be
   altered in database without an intent.
#. **Use image boxes in your templates**. For the thumbnails, use boxes.
   The snippet below shows how you can embed photos using boxes in an object
   box we used in :ref:`features-category-detail` section.

    .. code-block:: html+django
    
        <!-- in page/box/listing.html -->
        <div class="article">
            <h2><a href="{{ object.get_absolute_url }}">{{ object }}</a></h2>
            {% if object.photo %}
                <a href="{{ object.get_absolute_url }}" title="{{ object.title }}">
                    {% box category_listing for object.photo %}{% endbox %}
                </a>
            {% endif %}
        </div>
        
#. **Use** ``img`` **templatetag to generate thumbnails**. When the photo is embedded,
   the last remaining step is to generate thumbnails so the photo will fit on 
   the page nicely. To do this, use ``{% img %}`` template tag.
   
   .. code-block:: html+django
   
       <!-- in page/box/content_type/photos.photo/category_listing.html -->
       {% load photos %}
    
       {% block image_tag %}
           {% img 200x100 for object as image %}
           <img src="{{ image.url }}" alt="{% firstof title object.title %}" width="{{ image.width }}" height="{{ image.height }}" />
       {% endblock %}
   
   It's a good habit to use format naming convention which describes the used
   dimensions (like the "200x100" used in example above) and attributes because:
   
   * It will minimize the number of formats you use and eliminate duplicates.
   * It will eliminate the threat that the same image is formatted twice
      with same parameters. 
   
   
.. _initial data: https://docs.djangoproject.com/en/dev/howto/initial-data/

.. _features-related:

Working with related objects
****************************

.. _features-what-are-related-objects:

What are related objects?
=========================

By related objects, we understand publishable objects which have some relation
between them. They can be related in various ways, for example:

* belong to the same category
* have a same topic
* have similar tags attached to them
* have same author
* have same source

Showing such related content is very common on news sites because it helps
to link the content and also, it is very SEO friendly. 

Ella has simple but powerful interface for querying such relations and the core
module also implements some basic ones.

.. _features-related-finders:

Related finders
===============

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

.. note::

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
``collected_so_far``        Default type of the box to use, can be overriden 
                            from the admin.
``only_from_same_site``     Boolean telling the function if only the objects
                            from the same site as ``obj`` is are required.
==========================  ================================================

Each finder is required to return up to the ``count`` of related objects. A valid
option is to return an empty list (``[]``) if no related exist.

Finders are responsible for taking care of duplicates and no duplicates should
be present in intersection of ``collected_so_far`` and what is returned by the
finder function. You can easily use ``if obj not in collected_so_far`` condition
to find duplicates.

.. _features-related-templatetag:

``{% related %}`` template tag
==============================

Related template tag is ment for simple access to the related queries from
within your templates. It fills up a given variable with list of publishable 
objects that were collected by finder functions. When no ``query_type`` is 
given, ``default`` will be used.

**Usage**::

    {% related <limit>[ query_type] [app.model, ...] for <object> as <result> %}
        
**Parameters**:

==================================  ================================================
Option                              Description
==================================  ================================================
``limit``                           Number of objects to retrieve.
``query_type``                      Named finder to resolve the related objects,
                                    falls back to ``settings.DEFAULT_RELATED_FINDER``
                                    when not specified.
``app.model``, ...                  List of allowed models, all if omitted.
``object``                          Object to get the related for.
``result``                          Store the resulting list in context under given
                                    name.
==================================  ================================================

**Examples**::
    
    {% related 10 for object as related_list %}
    {% related 10 directly articles.article, galleries.gallery for object as related_list %}

.. _features-syndication:

Syndication - ATOM and his RSS friend
*************************************

.. _features-incorporating-plugins:

Incorporating plugins
*********************

.. _features-extending-metadata:

Extending category/publishable metadata
***************************************

.. _features-caching:

Caching
*******

.. _features-double-render:

Double rendering
================

.. _features-deployments:

Deployment
**********
