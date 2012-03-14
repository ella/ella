.. highlightlang:: html+django

.. _common-gotchas:

Common gotchas & FAQs
#####################

This section tries to present frequent problems Ella users run into. It provides
solutions for those problems. Hopefully, it will enhance you understanding for
doing the things Ella-way. 

.. _common-gotchas-creating-site-menus:

Creating site navigation
************************

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
        root = Category.objects.get_by_tree_path(slug)
        
        return {
            'slug': slug,
            'root': root,
            'current_root': category.get_root_category() if category is not None else None,    
            'current': category,
            'sub': root.get_children()
        }

Next, create the template for the menu part itself::

    {% load my_tags %}
    <li{% ifequal current.get_root_category root %} class="active"{% endifequal %}>
        <a href='{{ root.get_absolute_url }}'>{{ root.title }}</a>
        
        {% if sub %}
            <ul{% ifnotequal current_root root %} class="hidden"{% endifnotequal %}>
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

One of the best things about Django is undoubtedly it's templating framework. 
And one of it's most powerful features is the `template inheritance`_. When
building up Django templates, you use so-called **blocks** which can then
be overriden in the child template which inherits from the parent template. 
When using Ella, it's very beneficial to take the full advantage of the
inheritance concept since the number of templates in large Ella websites
can grow up significantly. Using the inheritance, you can very effectively
write as little code as possible. Here are some hints you may found useful:

* Always write the base template for object and category detail pages. Try 
  to put there as much shared code as possible.
* In you base template, don't hesitate to define many blocks so the child
  templates won't need to override big pieces of code. 
* It often make sense to put almost all parts of the base template into blocks.
  This applies for titles, descriptions, perexes, comment sections, object tools
  and so on. The more you allow to override, the smaller the child template will
  be.
* When dealing with content used in more than one template type or
  when it's hard to keep the inheritance scheme for some reason, use
  ``{% include %}`` and put those pieces of content in reusable snippets in 
  your ``inclusion_tags`` template subdirectory. A common use case scenario
  for this can be a right sidebar. Consider following example of reusable
  right col template. First, define the base ``rightcol.html`` template::
  
        <!-- in page/inclusion_tags/rightcol.html -->
        {% block rightcol_top %}{% endblock %}
        
        {% block rightcol_top_articles %}
            ... code showing top articles ..
        {% endblock %}
        
        {% block rightcol_category_poll %}
            ... code showing poll related to the category ...
        {% endblock %}
        
        {% block rightcol_bottom %}{% endblock %}
        
  This template contains the the stuff a sidebar can contain with possibility
  to add your own stuff to the top and to the bottom of it. Next define
  child templates of the ``rightcol.html`` for homepage and common category:: 
        
        <!-- in page/inclusion_tags/rightcol_hp.html -->
        {% extends "page/inclusion_tags/rightcol.html" %}
        
        {% block rightcol_top %}
            ... some special code to add on top of the right col ...
        {% endblock %}
        
        <!-- in page/inclusion_tags/rightcol_category.html -->
        {% extends "page/inclusion_tags/rightcol.html" %}
        
        {% block rightcol_top_articles %}{% endblock %}
  
  For the purpose of this example, we added a special piece of code at the top
  of the sidebar in homepage and turned off the displaying of top articles
  in common categories. In real-world situation, your intents will be probably 
  little different, but for the need of demonstration, this is sufficent. 
  Finally, put following piece of code in your base ``category.html``::
  
        <!-- in page/category.html -->
        {% block rightcol %}
            <div id="sidebar">
                {% block rightcol_content %}
                    {% if is_homepage %}
                        {% include "inc/rightcol_hp.html" %}
                    {% else %}
                        {% include "inc/rightcol_category.html" %}
                    {% endif %}
                {% endblock %}
            </div>
        {% endblock %}

  In the main category template, we can easily implement a default behavior
  without need to duplicate a single line of code.
* Every time you find yourself duplicating a HTML code, try to think if some
  kind of inheritance wouldn't help you avoid doing so. In most cases, this
  would be true.

.. _template inheritance: https://docs.djangoproject.com/en/dev/topics/templates/#template-inheritance 

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

TODO: create ella-haystack and be done with it.
