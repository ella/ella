.. _reference-templates:

Template overview
#################

This doc part is ment as quick reference for templates that Ella uses. The 
details on the template usage are kept in the section related to the each
of the templates presented. 

Object detail templates
***********************

This table shows the fallback used when selecting the right template for an
object. Note how the most specific template is searched for first. When 
no such template is found, Ella tries the find second-most specific and so on.

As a criterion for selection, two things are considered:

* Object's ``ContentType``, specifically ``CONTENT_TYPE_NAME`` which is defined
  as ``app_label.model_label``.
* ``path`` attribute of the ``Category`` which object belongs to.

=====================================================================  ============================================
Path                                                                   Description
=====================================================================  ============================================
**page/category/[PATH]/content_type/[CONTENT_TYPE_NAME]/object.html**  First template to try (category and content-specific)
                                                                       when rendering a ``Publishable`` detail.
**page/content_type/[CONTENT_TYPE_NAME]/object.html**                  Content-type specific template to try
                                                                       when rendering a ``Publishable`` detail.
**page/category/[PATH]/object.html**                                   Category-specific template to try when
                                                                       rendering a ``Publishable`` detail. 
**page/object.html**                                                   Fallback for rendering a ``Publishable`` detail
                                                                       page such as article content, see
                                                                       :ref:`features-object-detail`.
=====================================================================  ============================================

Category detail templates
*************************

Following table shows the template path prototypes used when selecting the 
suitable template for a category detail. Ella tries to find 
a correct template by inspecting the ``path`` attribute of the given 
``Category`` object.

.. note::
    
    The **category.html** can be overriden for specific categories via 
    administration. This will affect the mentioned fallback so that 
    instead of **category.html** Ella will search for **[OVERRIDEN_NAME].html**
    where [OVERRIDEN_NAME] stands for name of the selected template.
    
    For the details, see :ref:`features-category-detail`.

=====================================================================  ============================================
Path                                                                   Description
=====================================================================  ============================================
**page/category/[PATH]/category.html**                                 Specific template for a category detail
                                                                       page.
**page/category.html**                                                 Fallback template for rendering
                                                                       a category detail page, category 
                                                                       listings, static pages.
=====================================================================  ============================================

Box templates
*************

Box templates are distinguised only by ``CONTENT_TYPE_NAME`` as described
above. The root for searching is in the ``box`` subdirectory of your 
templates. Also, boxes are **named** so that the name of the template
searched is directly related to the **name of the box** being rendered.

=====================================================================  ============================================
Path                                                                   Description
=====================================================================  ============================================
**box/content_type/[CONTENT_TYPE_NAME]/[BOX_NAME].html**               Content-type specific template for a box
                                                                       named [BOX_NAME].
**box/[BOX_NAME].html**                                                Named template for a box without any specific
                                                                       content type. These are boxes that are same
                                                                       for most of publishables.
**box/box.html**                                                       Fallback template for
                                                                       :func:`box templatetag<ella.core.templatetags.core.do_box>`
                                                                       when no specific template for box is found.
=====================================================================  ============================================

Listing templates
*****************

Templates for listings (see :ref:`features-category-archives`) follow same rules
as categories with the only difference is that a **listing.html** is used
as template name.

Other templates
***************

=====================================================================  ============================================
Path                                                                   Description
=====================================================================  ============================================
**inclusion_tags/paginator.html**                                      Template for rendering pagination when
                                                                       listing a category content. Used by 
                                                                       :func:`paginator<ella.core.templatetags.pagination.paginator>`
                                                                       templatetag.
**404.html**                                                           Used to show user-friendly HTTP 404 page.
**500.html**                                                           Used to show user-friendly HTTP 500 page.
**base.html**                                                          Not required, but convention in Django apps
                                                                       is that this is the **base layout template**.
=====================================================================  ============================================

As mentioned in :ref:`features-template-fallback-mechanisms`, when finding
the suitable template, Ella uses smart template fallback for category, object
and box templates so that the ones listed above are only used as last resort.
Please refer there for the details on how Ella decides which template to use.