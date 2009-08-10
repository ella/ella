.. _positions:

=========
Positions
=========

Position as understood by this application is a part of the template with
content specific for category in which the template is rendered. It allows
designers to specify areas of the template to be overriden by the users via the
admin interface. Position is identified by it's name.

Purpose of a position is primarilly to display objects in form of a box, but it
can also be used to insert raw HTML into the template.


Features
========

Basic features:

**inheritance**
    When called from the template tag, the application will first try and
    locate the active position for the given category, then, if such position
    is not available, it will locate active position in the closest ancestor of
    the category. This behavior can be overriden by the nofallback argument to
    the templatetag.

**tied to objects or raw HTML**
    You can either define a generic foreign key to any object whose box you
    wish to display instead of the templatetag or, if the generic foreign key
    is empty, raw HTML that you wish to insert.

**ifposition templatetag**
    You can check if any position for a given set of names is active using the
    ifposition templatetag.

Usage
=====

Position is defined in the admin interface and used from the templates via two
templatetags.

{% position %}
--------------

Render a given position for category.

Syntax::

    {% position POSITION_NAME for CATEGORY [using BOX_TYPE] [nofallback] %}
      ...
    {% endposition %}

Parameters:

    ==========================  ================================================
    Name                        Description
    ==========================  ================================================
    ``POSITION_NAME``           Name of the position to lookup 
    ``CATEGORY``                The category for which to render the position - 
                                either a ``Category`` instance or category's
                                ``slug``.
    ``BOX_TYPE``                Default type of the box to use, can be overriden 
                                from the admin.
    ``nofallback``              If present, do not fall back to parent categories
    ==========================  ================================================


Text inside the tag (between ``{% position %}`` and ``{% endposition %}``) is
passed to ``Box`` used for rendering the object. This can also be overriden
from the database.

    
{% ifposition %}
----------------

Render template according to the availability of given position names within
given category.

Syntax::

    {% ifposition POSITION_NAME ... for CATEGORY [nofallback] %}
      present
    {% else %}
      not there
    {% endifposition %}

Renders 'present' if any of the space separated position name is active for the
given category, 'not there' otherwise.

