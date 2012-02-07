.. _common-gotchas:

.. highlightlang:: html+django

Common gotchas & FAQs
#####################

This section tries to present frequent problems Ella users run into. It provides
solutions for those problems. Hopefully, it will enhance you understanding for
doing the things Ella-way. 

.. _common-gotchas-creating-site-menus:

Creating site menus
*******************

A common situation. Site needs a **global menu which consists of links** to categories
and/or static pages. The question is: how do we do such a thing in Ella? The
answer is suprisingly simple. Use **positions** mate! Using positions, it's 
very simple to implement a site menu that can be edited via admin interface and
fast as lightning thanks to caching mechanisms. Have a look at following template::

    <!-- in position called "sitemenu" -->
    {% load my_tags cache %}
    
    {% cache CACHE_TIMEOUT "mainmenu" request.META.PATH_INFO %}
    <div id="menu">
        <ul>
            <li class='home'><a href="/" title="Homepage">Homepage</a></li>
            
            {% render_menu_part "news" %}
            {% render_menu_part "economics" %}
            {% render_menu_part "regional" %}
        </ul>
    </div>
    {% endcache %}
    
This snippet can be in position's ``text`` field (so it will be considered a
raw html) and renders two-level site menu with highlighting what is currently
active. It does so by using ``category`` in context and the responsible
code for this is custom ``{% render_menu_part %}`` inclusion tag. New items
can be added very easily. Each link is bound to a ``Category`` object using
it's **slug**.

.. code-block:: python

    @register.inclusion_tag('inc/menu_part.html', takes_context=True)
    def render_menu_part(context, slug):
        category = context.get('category', None)
        current_root = category.tree_parent \
            if category is not None and category.tree_parent_id and category.tree_parent.tree_parent_id \
            else category
        root = get_cached_object(Category, tree_path=slug)
        
        return {
            'slug': slug,
            'root': root,
            'current_root': current_root,    
            'current': category,
            'sub': get_cached_list(Category, tree_parent=root)
        }

Next, create the template for the menu part itself::

    {% load my_tags %}
    <li{% ifequal current_root.slug root.slug %} class="active"{% endifequal %}>
        <a href='{{ root.get_absolute_url }}'>{{ root.title }}</a>
        
        {% if sub %}
            <ul{% ifnotequal current_root.slug root.slug %} class="hidden"{% endifnotequal %}>
                {% for cat in sub %}
                    <li{% ifequal current cat %} class="active"{% endifequal %}>
                        <a href="{{ cat.get_absolute_url }}">{{ cat.title }}</a>
                    </li>
                {% endfor %}
            </ul>
        {% endif %}
    </li> 

The last step is to add position to the base template so that it will be shown
on each page::

    <!-- in page/base.html -->
    {% load positions %}
    ...
    {% block sitemenu %}
        {% ifposition sitemenu %}
            {% position sitemenu %}{% endposition %}
        {% endifposition %}
    {% endblock %}
    ...

.. _common-gotchas-sidebars:

Category-specific sidebars
**************************

Sidebars to show information related to the currently active category. This
can be a category-related poll, most interesting articles by editors choice
or something completely different.

Answer for this question is the same as in previous question. Use **positions**!
If you are not sure how to do it, please refer to :ref:`features-positions`.

.. _common-gotchas-taking-advantage-of-inheritance:

Taking advantage of template inheritance
****************************************

.. _common-gotchas-static-pages:

Static pages that don't ever change
***********************************

Content-heavy websites usually don't build it's success on lot of static pages.
However, there are always some a Ella is ready to provide effective weapons
to get rid of them.

The key here is to use ``Category`` and define a custom template, e.g.
``staticpage.html`` to use when you need to use the category as static page.
The reasoning for this is that categories already have nice, SEO-friendly URLs
and it would simply be unnecessary overhead to create a special solution for 
this. You can put you content to ``Category.content`` field which was added
for that purpose. Then simply use something like this::

    <!-- in page/staticpage.html -->
    {% extends "page/base.html" %}
    
    {% block content %}
        <h1>{{ category }}</h1>
        {% render category.content %}
    {% endblock %}

.. _common-gotchas-integrating-search:

Integrating searching
*********************
