Ella CMS
########

`Ella`_ is a Content Management System based on `Python`_ web framework
`Django`_ with a main focus on high-traffic news websites and Internet
magazines.

It is composed from several modules:

    * **Ella core** is the main module which links the rest together. It
      defines architecture on which other modules are built but doesn't do
      anything really usefull all alone.
    * **Ella core plugins** are plugins that are shipped in one package
      together with Ella. There are **articles** and **positions** which 
      we consider to be a basic toolbox for each Ella site.
    * **Other Ella plugins** are standalone applications (and therfore
      not shipped with the core) that provide some
      specific functionality using **Ella's architecture**. We can mention
      polls, galleries, quizes and many more.
      
Feature highlights:

    * Simple organization of content based on categories
    * Efficent implementation of the published content
    * In-build photo formating backend
    * Django-admin ready
    * Plugin system
    * Flexibile
    * Scalable
    * Extensible
    * Caching-friendly
    * Well tested
    * Proven in production environment

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
    developer
    html_coder
    features
    plugins/index
    reference
    common_gotchas
    settings


Sites using Ella
****************

Ella is getting more and more popular. Here are some sites that take advantage
of it:

* `tested.com <http://www.tested.com>`_
* `mom.me <http://mom.me>`_
* `Investicniweb.cz <http://www.investicniweb.cz>`_
* `MarieClaire.cz <http://www.marieclaire.cz>`_
* `Dumazahrada.cz <http://www.dumazahrada.cz>`_
* `Květy <http://kvety.kafe.cz>`_
* `Vlasta <http://www.vlasta.cz>`_
* `Crazycafe.cz <http://www.crazycafe.cz>`_
* `EquiTV.cz <http://equitv.cz/>`_
* `Vaquero.cz <http://vaquero.cz/>`_
* `Ranch Bystrá <http://ranchbystra.cz/>`_
* `pyvec.org <http://pyvec.org>`_

Community
*********

* Mailing list: ella-project@googlegroups.com
* IRC channel: #ellacms@freenode.net

License
*******

Ella is licensed under the BSD licence. It utilizes many conceps and examples
from django itself, `djangosnippets`_ and several other open-source project. We
would like to thank the community around Django for the huge amount of great
quality code they share with other Djangonauts. We are proud to be part of that
community and hope that somebody will find this project helpfull.

.. _djangosnippets: http://www.djangosnippets.org


