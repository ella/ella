Ella CMS
########

Ella is opensource CMS based on Django framework, designed for flexibility.

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
      
**Feature highlights**:

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
    
News
****

Currently, we released the **3.x version** which features a **major cleanup** 
of the code a **removal of unneeded dependencies**.

More news are on the way as we are going to make a nicely-tailored admin 
specifically made for the need of news writers and editors. 
    
Docs
****

Docs are hosted on readthedocs.org, go to http://ella.rtfd.org.

Community
*********

* We stick with github to manage the issues, see https://github.com/ella/ella/issues.
* mailing list can be found at ella-project@googlegroups.com
* IRC channel #ellacms on freenode.net

Quickstart
**********

Have a look at the docs: http://readthedocs.org/docs/ella/en/latest/quickstart.html.

Build status
************

:Master branch:

  .. image:: https://secure.travis-ci.org/ella/ella.png
     :alt: Travis CI - Distributed build platform for the open source community
     :target: http://travis-ci.org/#!/ella/ella

