.. _tutorial-4:

===============================
Deploying your Ella application
===============================

.. note::
    This is another part of Ella tutorial, but the techniques and actions
    described here should work for any Django project/application out there.

    Most of what is used here can be found in our `django-base-project`_
    template.

So far in our tutorial we got to a state where we have a fully working
application, on localhost that is. Since you probably won't be running it from
there, you need to move it to another server. The moving itself isn't the
problem, but managing different configurations (``settings.py``) and keeping
your database in order (migrations) might prove challenging. I want to describe
some of the techniques we use to help us manage multiple environments and,
possibly, multiple projects using the same database.

.. _django-base-project: http://github.com/ella/django-base-project

``settings.py``
===============

So far we have everything in a single ``settings.py`` file, all the
configuration options - those that we need to run our project as well as those
that cope with our current environment specifically. To help with this we will
split our ``ellablog.settings`` module into a package::

    mkdir ellablog/settings
    touch ellablog/settings/__init__.py
    mv ellablog/settings.py ellablog/settings/base.py

with ``__init__.py`` containing::

    from ellablog.settings.base import *

This didn't help our problem, but it gave us some more room to organize things
a bit better. Now let's split the configuration into more parts:

    * ``base.py`` is responsible for setting all the variables we *need* for
      our project to run, mainly ``INSTALLED_APPS``, ``TEMPLATE_LOADERS``,
      ``TEMPLATE_CONTEXT_PROCESSORS``

    * ``config.py`` will contain the configurable parts, mainly db and cache
      definitions, server and filesystem paths (``MEDIA_ROOT``, ``MEDIA_URL``),
      SMTP settings, ...

    * ``local.py`` won't get committed to our VCS but, if present, will provide
      overrides specific to some environment (dev/test/production)

    * ``__init__.py`` will actually do all the work, it will import all the
      submodules in the proper order (as listed) to assure correct values are
      being used

Just to provide some more extensibility, we will also add a simple mechanism
that will allow us to store ``config.py`` in a separate location
(``/etc/ella``) on our server (that way it won't get overwritten during every
install). Also it will initiate python's ``logging`` module, if any of the
configuration files ask for it. So the final ``__init__.py`` will look::

    # logging init - this options should be overriden somewhere
    LOGGING_CONFIG_FILE = None
    
    # load base configuration for whole app
    from ellablog.settings.base import *
    
    # load some dev env configuration options
    from ellablog.settings.config import *
    
    # try to import some settings from /etc/
    import sys 
    sys.path.insert(0, '/etc/ella')
    try:
        from ellablog_config import *
    except ImportError:
        pass
    del sys.path[0]
    
    # load any settings for local development
    try:
        from ellablog.settings.local import *
    except ImportError:
        pass

    if LOGGING_CONFIG_FILE:
        import logging.config
        logging.config.fileConfig(LOGGING_CONFIG_FILE)


Fixtures and custom commands
============================

When you deploy your new blog site, if you want to start fresh after playing
around with the admin or if you decide to switch database backends, you don't
want to recreate all your objects again in the database. That's why we will
create a `fixture`_ with all the basic data and have it automatically loaded
into the database every time it gets created. Django will automatically load
any fixture called ``initial_data`` in any application's ``fixtures``
subdirectory so we need to create an application to store our fixture, let's
call it ``service`` and create our fixture there::

    python manage.py startapp service
    mkdir service/fixtures
    python manage.py auth.User core articles --indent 4 > service/fixtures/inital_data.json

Next we just need to add it to our ``INSTALLED_APPS``::

    INSTALLED_APPS = [
        ...
        'ellablog.service',
    ]

Our newly created application can also be useful if you wanted to add some
`custom management commands`_.


Static files
============

using

project

admin


Migrations
==========

south, on deploy
