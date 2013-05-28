.. _features:

Features
########

This section presents **core Ella features**. It's recommended to all of the
user base. Some parts might be a little heavy for html coders though. It goes
from the most basic aspects to the more and more specialized ones. It tries to
show the concepts by examples and doesn't go into the deep descriptions of
the API. If you are looking for reference instead, go to the :ref:`reference`.

As a rule of the thumb, all sections up to the :ref:`features-related` are
recommended for an every-day Ella user.

.. _features-template-fallback-mechanisms:

Template fallback mechanisms
****************************

Templates for rendering categories and publishable objects use fallback mechanism
to provide you full control over what is rendered with minimum effort required.

When selecting template to use for given URL, Ella does several things based
on what we are dealing with. However, in both cases there is final fallback to
default templates which are:

* **category.html** for a category template
* **object.html** for an object template

.. note::

    Under some circumstances, **category.html** can be overriden, see
    :ref:`features-category-custom-templates` for more details.

Selecting template for a category
=================================

When selecting templates for a rendering of category, Ella uses this set of
rules:

#. Look at the ``tree_path``. Try to find a template in
   ``page/category/[TREE_PATH]/category.html``.

   Example:

       **http://www.example.com/category/subcategory/**
           Ella would first try to find ``page/category/category/subcategory/category.html``.

#. If template was not found in previous step, try to find the template
   of an direct ancestor providing we have one and it's not the root category.

   Examples:

       **http://www.example.com/category/subcategory/subsubcategory/**
           First, try ``page/category/category/subcategory/category.html``,
           next try ``page/category/category/category.html`` and stop because the
           category ``"category"`` is the main one.

       **http://www.example.com/category/subcategory/**
           Try ``page/category/category/category.html`` and stop.

       **http://www.example.com/category/**
           Would not try anything, we are already in main category.

       **http://www.example.com/**
           Would not try anything, we are in root.

#. If template wasn't found yet, use default template (which is
   ``page/category.html`` in most cases).

Selecting template for an object
================================

Selecting template for an object adds even more possibilities for the developer.
It also uses ``content_type`` in form of ``app_label.model_label`` (both
lowercased). Example would be: ``articles.article``, ``videos.video`` and so on.

#. Try to find a template in
   ``page/category/[TREE_PATH]/content_type/[CONTENT_TYPE]/object.html``.

#. Try to find a template in
   ``page/content_type/[CONTENT_TYPE]/object.html``.

#. Continue in the same way as when selecting a category template except for
   using ``object.html`` instead of ``category.html``.

Selecting template for a box
============================

Lookup for boxes is done in ``"box"`` subdirectory. It then works exactly
the same as for objects, except that the template name is the **name of the
box** being rendered and last resort is template ``box/box.html``.

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

==================================  ============================================
Key                                 Value
==================================  ============================================
``category``                        ``Category`` object itself.
``is_homepage``                     Flag telling you if this is a homepage, see
                                    :ref:`features-category-homepages`.
``is_title_page``                   Boolean telling you if this is the first
                                    page of the listing/archive.
``is_paginated``                    Boolean which is ``True`` more pages are
                                    available.
``results_per_page``                Number of objects per page.
``page``                            Current page shown.
``listings``                        Objects listed in the ``category`` for this
                                    page.
``content_type``                    If filtering by Content Type is active,
                                    this will hold the ``ContentType`` instance.
``content_type_name``               Verbose name of content type if Content Type
                                    filtering takes place.
==================================  ============================================

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
                {% box listing for l.publishable %}{% endbox %}
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

.. note::

    To be consistent with the Ella guidelines, please always use ``category.html``
    as your base category template.

Next, create the **base template**. That would be ``category.html``. It would
be used, when not set otherwise in your Ella administration:

.. code-block:: html+django

    <!-- in page/category.html -->
    {% extends "page/base.html" %}

    {% block object_listing %}
        <!-- show 4 boxes with big images -->
        {% listing 4 for category as category_listing %}
        {% for l in category_listing %}
            {% box listing_big_image for l.publishable %}{% endbox %}
        {% endfor %}

        <!-- show 6 more regular boxes -->
        {% listing 6 from 4 for category as category_listing %}
        {% for l in category_listing %}
            {% box listing for l.publishable %}{% endbox %}
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
            {% box listing for l.publishable %}{% endbox %}
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
            {% box listing_no_perex for l.publishable %}{% endbox %}
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

Object detail URL
=================

The URL of ``Publishable`` object detail depends on publication type. As we
already mentioned in :ref:`tutorial`, there are two:

* **time-based** publication is limited by ``publish_from`` - ``publish_to``
  period. Outside of these time boundaries, object won't be reachable
  on the website. Most websites only use ``publish_from`` so that the object
  won't disappear.
* **static** publication is not limited by time and thus it is unlimited and
  permanent. Such object will be always reachable on the website.

With **time-based** publications, objects are given a date stamp in the URL
so the namespaces clashes doesn't happen very often. URL structure goes like::

    /category/tree/path/[YEAR]/[MONTH]/[DAY]/[CONTENT_TYPE_NAME]/slug/

So for an example, ``/about/2007/08/11/articles/ella-first-in-production/`` could
be proper result of **time-based** publication.

With **static** publication, no date stamp is used. Instead, **object's primary
key is prepended before slug** to avoid name conflicts. URL structure looks like
this::

    /category/tree/path/[CONTENT_TYPE_NAME]/[PK]-slug/

And a valid result could be ``/about/articles/1-ella-first-in-production/``.

.. _features-category-archives:

Archive pages
*************

.. _features-markup:

Rich-text fields: using WYSIWYG editors or a markup language
************************************************************

.. _features-custom-views:

Integrating custom views
************************

Ella doesn't force you to make your views any prescribed way. You can easily
create any Django application and add it to your project standard Django way
and Ella won't stand in way.

However, if you try to extend the functionality of the framework itself,
you might want to have a look at :ref:`Ella plugins <features-incorporating-plugins>`
which offer several simple interface for extending the Ella.

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

.. note::
    This feature is part of `ella.positions` app and thus needs to be added to
    `INSTALLED_APPS` before use.

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

Renders '*POSITION EXISTS*!' if any of the space separated position name is active for the
given category, '*NO POSITION DEFINED!*' otherwise.

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


Generating thumbnails in the tempalates
=======================================

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
particularly ``url`` method and ``width`` and ``height``.

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

        <!-- in box/listing.html -->
        <div class="article">
            <h2><a href="{{ object.get_absolute_url }}">{{ object }}</a></h2>
            {% if object.photo %}
                <a href="{{ object.get_absolute_url }}" title="{{ object.title }}">
                    {% box category_listing for object.photo %}{% endbox %}
                </a>
            {% endif %}
        </div>

#. **Use** ``image`` **templatetag to generate thumbnails**. When the photo is embedded,
   the last remaining step is to generate thumbnails so the photo will fit on
   the page nicely. To do this, use ``{% image %}`` template tag.

   .. code-block:: html+django

       <!-- in box/content_type/photos.photo/category_listing.html -->
       {% load photos %}

       {% block image_tag %}
           {% image object in "200x100" as image %}
           <img src="{{ image.url }}" alt="{% firstof title object.title %}" width="{{ image.width }}" height="{{ image.height }}" />
       {% endblock %}

.. note::
   It's a good habit to use format naming convention which describes the used
   dimensions (like the "*200x100*" used in example above) and attributes because:

   * It will minimize the number of formats you use and eliminate duplicates.
   * It will eliminate the threat that the same image is formatted twice with
     same parameters.


.. _initial data: https://docs.djangoproject.com/en/dev/howto/initial-data/

.. _features-photo-placeholders:

Using placeholder images during development
===========================================

It is quite common that during development of the Ella application, one doesn't
always have all the photos stated in database on his HDD. This can happen
when you share one database dump with co-workers and someone adds new articles
etc.

In order to show at least something, Ella provides debugging setting which
will replace the missing image files by **placeholder images**. You can enable
this by setting ``PHOTOS_DEBUG = True`` in your project settings. By default,
Ella will use web service http://placehold.it to generate the images. Optionally,
you can use your custom placeholder service by changing the ``PHOTOS_DEBUG_PLACEHOLDER_PROVIDER_TEMPLATE``
to your own. Use something like this::

    DEBUG_PLACEHOLDER_PROVIDER_TEMPLATE = 'http://placehold.it/%(width)sx%(height)s'

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

.. _features-related-templatetag:

``{% related %}`` template tag
==============================

Related template tag is ment for simple access to the related queries from
within your templates. It fills up a given variable with list of publishable
objects that were collected by the finder functions defined for the project(see
:ref:`plugins-related-finders` for more details). When no ``query_type`` is
given, ``default`` will be used.

**Usage**:

.. code-block:: html+django

    {% related <limit>[ query_type] [app.model, ...] for <object> as <result> %}

**Parameters**:

==================================  ================================================
Option                              Description
==================================  ================================================
``limit``                           Number of objects to retrieve.
``query_type``                      Named finder to resolve the related objects,
                                    falls back to ``default`` when not specified.
``app.model``, ...                  List of allowed models, all if omitted.
``object``                          Object to get the related for.
``result``                          Store the resulting list in context under given
                                    name.
==================================  ================================================

**Examples**:

.. code-block:: html+django

    {% related 10 for object as related_list %}
    {% related 10 directly articles.article, galleries.gallery for object as related_list %}

.. note::

    Please note that you can define new related finders very easily and instantly
    call them in your templates. Whenever you need to query for some object
    list by some relation, it's the use case for a *custom related finder*.

.. _features-syndication:

Syndication - ATOM and his RSS friend
*************************************

Ella has automatic syndication support **out of the box**. For each category,
there are RSS a ATOM feeds automatically available on::

    www.example.com/feeds/rss/[CATEGORY_TREE_PATH]/

and::

    www.example.com/feeds/atom/[CATEGORY_TREE_PATH]/

respectively.

Ella uses `Django syndication feed framework`_ internally to render the feeds.
Default number of objects in feed is set to **10** by ``RSS_NUM_IN_FEED``
setting. You can override this setting it to different value in your
``settings.py``. Also, you can define an `enclosure`_ format by setting
``RSS_ENCLOSURE_PHOTO_FORMAT`` which defaults to ``None``.
The value is expected as ``Format`` instance name. If you set this to ``None``
(or don't set it at all), no enclosures will be used.

The feed title and description defaults to category ``title`` attribute. If you
need to override this, use :ref:`app_data <features-extending-metadata>` and
make sure you set following::

    category.app_data['syndication'] = {
        'title': 'My feed title',
        'description': 'My feed description'
    }

You can do this through Django administration.

.. _Django syndication feed framework: https://docs.djangoproject.com/en/dev/ref/contrib/syndication/
.. _enclosure: https://docs.djangoproject.com/en/dev/ref/contrib/syndication/#enclosures


.. _features-incorporating-plugins:

Incorporating plugins
*********************

Ella design is as lightweight as possible. Prefered way of extending it's
functions is via **plugins**. Ella provides great flexibility when it comes
to plugin possibilities. You can for example:

* Add your custom ``Publishable`` subclasses.
* Create custom ``Box`` classes for the new publishables.
* Add new actions over the ``Publishable`` objects.
* Customize bundled workflow when rendering the content.

We've dedicated :ref:`whole section for plugins <plugins>`, because it's an
important topic and almost every project has it's specific needs. So, for
details, go to :ref:`plugins`.

.. _features-extending-metadata:

Extending category/publishable metadata
***************************************

Since Ella has quite a long history behind it, we've gathered lot of experience
from previous fails. One such experience is that **almost every project needs
to add aditional data on the bundled models**. This can be done in lot of
various ways because of Python's great possibilities, but more or less, it's
a dark magic or monkey patching. This is not nice and violates the Django
core principle: *explicit is better then implicit*. To fix this up, we've
added possibility to add arbitrary data on ``Publishable``, ``Category`` and ``Photo``
models programatically.

Each of the mentioned models has one `JSONField`_ subclass ``AppDataField``
called ``app_data`` which can hold any information you need. It has some
limitations though:

* It's not possible to **perform efficent queries** over the defined fiels. If
  you needed it, add ``OneToOne`` relation to your custom model instead.
* You are **responsible of setting the fields correctly**, no validation measures
  are placed on that field so that the data might be corrupted if not used
  properly.

``AppDataField`` acts the same way as regular Python ``dict`` object. You can
store any data structure you like provided it's serializable by Django's JSON
`encoder`_.

Conventions
===========

``AppDataField`` recognizes namespaces for different applications. The access
is not limited though so that any application can access any namespace. The
namespace is a simple first-level dict key (e.g. 'emailing' or 'my_articles'
in the following examples).

To avoid name clashes, we encourage you to follow this convention so that all your
custom data is stored by using a **key** which coresponds to the app label
of aplication storing the data, such as::

    # in app "emailing"
    p = Publishable()
    p.app_data['emailing'] = {'sent': False}

    # in app "my_articles"
    p = Publishable()
    p.app_data['my_articles'] = {'custom_title': 'Foobar'}

.. _JSONField: https://github.com/bradjasper/django-jsonfield
.. _encoder: https://docs.djangoproject.com/en/dev/topics/serialization/#id2


Custom container classes
========================

By default, Ella returns an ``AppDataContainer`` class when you access a
namespace. This is simply a dict subclass with no additional data except
for the information about the model class it is bound to. However, you
can provide your own classess for the namespaces. This allows you to create
methods working with the your custom data. For example, you can have
``CommentsDataContainer`` for your comments application which can provide
methods like ``comment_count``.

Registering your custom container class is very simple. The formula is::

    from app_data import app_registry
    app_registry.register('comments', CommentsDataContainer, Publishable)

Unregistration works the same way::

    app_registry.unregister('comments', Publishable)
    app_registry.register('comments', SomeOtherDataContainer, Publishable)

.. _features-caching:

Caching
*******

.. _features-double-render:

Double rendering
================

.. _features-deployment:

Deployment
**********

