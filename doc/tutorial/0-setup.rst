.. _tutorial-0:

===============
Setting up Ella
===============

This tutorial will guide you through the process of creating and deploying an
Ella-based site. Since Ella is a CMS, we will create a blog. This first step
will take us through setting up our environment, installing all the
dependencies and creating the actual project. Before you dive into it, we
suggest you go through the official `Django tutorial`_ to get yourself familiar
with Django since we will be relying on that.


Dependencies
============

We assume that ``python``, ``setuptools`` and ``python-imaging`` (``PIL``) are
installed on your system directly since they can be non-trivial to install the
python way. We will be working with `pip`_ and `virtualenv`_ which are great
tools for any python project.

.. note::
    We will not cover any version control, but we
    strongly advise you use some (we prefer `GIT`_) to keep track of your emerging
    project. Also the code examples supplied are available as a GIT repository.

First we need to install ``virtualenv`` (under root)::

    easy_install virtualenv

Now we can create and activate a virtualenv where our project and all related
code will reside::

    virtualenv ella_sandbox
    source ella_sandbox/bin/activate

Next let's install all the dependencies we will need using ``pip``::

    pip install django
    pip install markdown2
    pip install setuptools_dummy
    pip install -e git://github.com/ella/django-markup.git#egg=django-markup
    pip install -e git://github.com/ella/ella.git#egg=ella

This should leave us with virtualenv containing everything necessary to develop
and run our project, so let's create it using the standard Django way::

    mkdir ellablog
    cd ellablog
    django-admin.py startproject ellablog

.. _Django tutorial: http://docs.djangoproject.com/en/dev/intro/tutorial01/
.. _pip: http://pip.openplans.org/
.. _virtualenv: http://pypi.python.org/pypi/virtualenv
.. _GIT: http://git-scm.com/

``settings.py``
===============

Our first step in actual code will be adding Ella to your project's
``INSTALLED_APPS`` along with some required settings, the resulting values
(unchanged values are omitted) should look::

    ...
    INSTALLED_APPS = (            
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

        'djangomarkup',
    )

    TEMPLATE_CONTEXT_PROCESSORS = ( 
        'django.core.context_processors.media',
        'django.core.context_processors.auth',
        'django.core.context_processors.request',
        'ella.newman.context_processors.newman_media',
    )
    NEWMAN_MEDIA_PREFIX = MEDIA_URL + 'newman/'

    DEFAULT_MARKUP = 'markdown'
    ...

Static files and templates need to be taken care of, so let's create
directories in our project called ``static`` and ``templates`` that will hold
our media and templates and alter ``settings.py`` accordingly::

    from os.path import join, dirname
    
    PROJECT_ROOT = dirname(__file__)

    MEDIA_ROOT = join(PROJECT_ROOT, 'static')
    MEDIA_URL = '/static/'

    TEMPLATE_DIRS = ( 
        join(PROJECT_ROOT, 'templates'),
    )


``urls.py``
===========

Last thing to configure is the URL mappings, we want to include ``newman``
(Ella's admin) and ``ella.core.urls`` but also create some mappings that will
serve our static files (and static files for admin) in the development server.
Note that these patterns are only defined if ``DEBUG`` mode is turned on since
we don't want to be using this setup in production.::
    
    from django.conf.urls.defaults import *
    from django.conf import settings 
    
    from ella import newman
    
    # make sure to import ella error handlers
    from ella.core.urls import handler404, handler500
    
    # register ella's admin
    newman.autodiscover()
    
    urlpatterns = patterns('',)
    
    if settings.DEBUG:
        # only use these urls in DEBUG mode, otherwise they should be handled by your web server
        from os.path import dirname, join, normpath
    
        import django, ella
    
        
        # static files from both admin apps
        ADMIN_ROOTS = ( 
            normpath(join(dirname(ella.__file__), 'newman', 'media')),
            normpath(join(dirname(django.__file__), 'contrib', 'admin', 'media')),
        )   
    
        # serve static files
        urlpatterns += patterns('',
            # newman specific files first
            (r'^%s/(?P<path>.*)$' % settings.NEWMAN_MEDIA_PREFIX.strip('/'), 'ella.utils.views.fallback_serve', {'document_roots': ADMIN_ROOTS}),
            # rest of the static files
            (r'^%s/(?P<path>.*)$' % settings.MEDIA_URL.strip('/'), 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
        )   
    
    
    # actual URL mappings
    urlpatterns += patterns('',
        (r'^newman/', include(newman.site.urls)),
        (r'^', include('ella.core.urls')),
    )


Database
========

Now just configure which database you wish to use (Ella supports all Django DB
backends) you can proceed with creating the database (don't forget to define
your admin user)::

    python manage.py syncdb

Congratulations, you should have a working Ella project. If you start the
development server and try to load the site's root, you should get a 404 error
- that's because we haven't created the site in the admin interface yet, that
will be covered in :ref:`second part of the tutorial <tutorial-1>`.

