========
Ella CMS
========

`Ella`_ is a Content Management System based on `Python`_ web framework `Django`_.
But for starting an application using Ella, only knowledge about adding Python
modules to PYTHONPATH is essential.

It is a set of Django applications designed to work together. Thus, for details
on deployment and configuration please refer to `Django documentation`_.

For creating site using Ella, working knowledge of Django and its templating
language is paramount. Rest is described in our :ref:`tutorial <tutorial-0>`.

.. _Ella: http://www.ellaproject.cz
.. _Python: http://www.python.org/
.. _Django: http://www.djangoproject.com/
.. _Django documentation: http://docs.djangoproject.com/en/dev/


Features
========

The system currently consists of:

Core application handling URLs, publication logic and provides all the tools for building content sites:

    * URL patterns and according views defining templates
    * mechanism for other application to inject themselves in the URL resolution
    * box templatetag that can display object of any type via a common interface
    * mechanism for publishing objects (defining URLs, listing objects in categories according to date and priorities)
    * various caching tools

Several content providing apps:

    * photos app with automatic format generation
    * articles
    * galleries containing arbitrary number of objects of any type
    * polls application that provides polls, quizes and contest models
    * etc..

Some tools to work with that content:

    * admin interface with advanced UI (newman)
    * comments (based on `django-threadedcomments`_) with threading and basic moderation
    * ratings app (being extracted into `django-ratings`_)
    * :ref:`positions` - a tool for editors to define what object should be visible in positions pre-defined by template designer

.. _django-threadedcomments: http://github.com/ericflo/django-threadedcomments
.. _django-ratings: http://github.com/ella/django-ratings


Documentation
=============

Tutorial: :ref:`tutorial-0` | :ref:`tutorial-1` | :ref:`tutorial-2` | :ref:`tutorial-3` | :ref:`tutorial-4`

Reference: :ref:`core-views` | :ref:`core-templatetags`

Applications: :ref:`positions`


License
=======

Ella is licensed under the BSD licence. It utilizes many conceps and examples
from django itself, `djangosnippets`_ and several other open-source project. We
would like to thank the community around Django for the huge amount of great
quality code they share with other Djangonauts. We are proud to be part of that
community and hope that somebody will find this project helpfull.

.. _djangosnippets: http://www.djangosnippets.org


.. toctree::
   :glob: 
   :hidden:

   tutorial/*  
   core/*
   positions

