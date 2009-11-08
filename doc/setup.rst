=====
Setup
=====

Ella is a set of standard django applications so in order to use it you first
need to create a django project and add those applications to
``INSTALLED_APPS`` along with their dependencies::

    INSTALLED_APPS = [
        ...
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.redirects',

        'ella.core',
        'ella.photos',
        'ella.newman',
        'ella.articles',
        ...
    ]

and define the URL mappings::

    # use ella's error handlers
    from ella.core.urls import handler404, handler500

    # newman instead of django.contrib.admin
    from ella import newman
    newman.autodiscover()

    urlpatterns += patterns('',
        (r'^newman/', include(newman.site.urls)),
        (r'^', include('ella.core.urls')),
    )

Next you have to suuply the templates, the minimal set of template you will need is:

    * ``page/category.html`` for category rendering, this will also render as
      your site's root ('/' - which is just root category's URL).

    * ``page/object.html`` all the object details rendering

    * ``page/listing.html`` archives and list of objects

    * ``page/404.html``, ``page/500.html`` the error templates

See :ref:`core-views` for views that render these templates and the context content.

.. warning::
    
    Ella's error handlers use ``RequestContext`` by default. If you have any
    logic in your context processors that might fail you should use your own
    ``handler500`` (do not import it in your ``urls.py``).
