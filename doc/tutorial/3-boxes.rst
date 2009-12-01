.. _tutorial-3:

===================
Enhancing templates
===================

.. highlightlang:: html+django

Since Ella is a regular Django application, even it's templates are just plain
Django templates. Therefore we just refer you to `other sources`_ to learn more
about the templating language and it's best practices, we will try to focus
just on ella-specific parts.

.. _other sources: http://docs.djangoproject.com/en/dev/#the-template-layer


Boxes
=====

First change we will make is abstract the rendering of the object listing on
category homepage and archive. To do this, ella provides a ``Box`` for
individual objects. It's primary use is as a :func:`templatetag
<ella.core.templatetags.core.do_box>`.  Boxes can be rendered for objects
accessible through a variable or through a database lookup::

    {% box <box_name> for <object> %}{% endbox %}
        or
    {% box <box_name> for <app.model> with <field> <value> %}{% endbox %}

What ``{% box %}`` does is a little more then fancy include - it retrieves the
object, find the appropriate template and renders that. Boxes are usually used
throughout an Ella site to provide maximum flexibility in rendering objects
and also for embedding objects into rich text fields stored in the database (in
text of an article for example). Some applications (:ref:`positions` for
example) also use boxes to represent objects.

To create our first box, we just need to create a template called
``box/listing.html`` containing::

    <p>
        <a href="{{ object.get_absolute_url }}">{{ object.title }}</a>
        {{ object.description|safe }}
    </p>

And change ``page/category.html`` to use the box instead of manually specifying
the output::

    <h1>Welcome to category {{ category.title }}</h1>
    <p>{{ category.description }}</p>
    
    {% for listing in listings %}
        {% box listing for listing.target %}{% endbox %}
    {% endfor %}



Overriding templates
====================

In :ref:`last step <tutorial-2>` we created a few templates that should suffice
for an entire site based on Ella. In real life you probably wouldn't want every
category and every object to share the same template. Ella provides a simple
mechanism to target your templates more directly.

Let's say that we want to create a specific template for rendering articles,
just create a template called
``page/content_type/articles.article/object.html`` and you are done - next time
you visit some article's URL, this template will get rendered instead of your
``page/object.html``. This template would be a good place to render the text of
an article for example::
    
    {% extends "page/object.html" %}
    {% block content %}
        {{ object.content.content|safe }}
    {% endblock %}

Now if you just define the appropriate block in your ``page/object.html``::

    <h1>{{ object.title }}</h1>
    <p>Published on {{ placement.publish_from|date }} in category: <a href="{{ category.get_absolute_url }}">{{ category }}</a></p>
    {{ object.description|safe }}
    {% block content %}{% endblock %}

You should be able to see your article's text on the web.

Another way you can override your templates is based on ``Category``. For
example if you want to create a custom template for your root category (and
your root category's slug is ``ella-blog``), just create one called
``page/category/ella-blog/category.html``::

    <h1>Welcome to site {{ category.site }}</h1>
    <p>{{ category.description }}</p>  
                                    
    {% for listing in listings %}
        {% box listing for listing.target %}{% endbox %}
    {% endfor %}

You will be greeted into the site and not your root category next time you
visit the root of your blog. Just create any subcategory to check it will
remain unaffected.

You can use the same simple mechanism (creating new templates) to cange the
look of your boxes for individual objects as well.

.. note::
    For more detailed explanation of all the possible template names, have a
    look at :ref:`views <core-views>` and :ref:`templatetags
    <core-templatetags>` documentation.


Now you have a working site and all necessary tools to built a fancy
ella-powered website, in :ref:`next step <tutorial-4>` we will show you how we
think it's best to layout your newly created application for easy deployment
and maintenance.

