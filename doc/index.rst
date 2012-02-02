Ella CMS
########

`Ella`_ is a Content Management System based on `Python`_ web framework
`Django`_.

It is composed from several modules:

    * **Ella core** is the main module which links the rest together. It
      defines architecture on which other modules are build but doesn't do
      anything really usefull all alone.
    * **Ella plugins** are standalone applications that provide some
      specific functionality using **Ella's architecture**. We can list for
      e.g. articles, polls, galleries, quizes.

For creating site using Ella, working knowledge of Django and its templating
language is required. It is therfore highly recommended to get familiar with
`Django`_ **before** you try to dwell into Ella. You can start in
`Django documentation`_.

.. _Ella: http://www.ellaproject.cz
.. _Python: http://www.python.org/
.. _Django: http://www.djangoproject.com/
.. _Django documentation: http://docs.djangoproject.com/en/dev/

Documentation
*************

Contents:

.. toctree::
    :maxdepth: 2
    :glob: 
   
    quickstart
    core
    features
    plugins
    common_gotchas
    settings


License
*******

Ella is licensed under the BSD licence. It utilizes many conceps and examples
from django itself, `djangosnippets`_ and several other open-source project. We
would like to thank the community around Django for the huge amount of great
quality code they share with other Djangonauts. We are proud to be part of that
community and hope that somebody will find this project helpfull.

.. _djangosnippets: http://www.djangosnippets.org


