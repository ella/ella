.. _plugins:

Plugins
#######

Ella tries to keep the core framework **as lightweight as possible**. This 
has very good reasons:

* it let's what is required for your app to **your decision**
* it minimizes the **dependencies** of core application
* it makes the development faster, because you can enhance your module
  while not needing to update the rest of the code
  
Because of this philosophy, **plugins** were introduced in version **3.0.0**.

======================
Basic plugin structure
======================

All Ella plugins come as Django applications bundled using setuptools. Each plugin
has dependency on the Ella's core, so Ella is always required and plugins can
hardly be used without it.

As Ella provides significant flexibility, plugins are able to do quite a lot of
magic, like following:

* Define custom ``Publishable`` objects via subclassing. For more details, see
  :ref:`plugins-subclassing-publishable`.
* Extend actions performed over the ``Publishable`` objects, for details, see 
  :ref:`plugins-adding-new-actions` section.
* Create custom ``Box`` classess for fine-tuned includes. This is discussed
  in detail in section :ref:`plugins-custom-boxes`.
* Hooking up with related finders, see :ref:`plugins-related-finders`.

.. _plugins-subclassing-publishable:

=======================
Subclassing Publishable
=======================

Due to the fact that ``Publishable`` is common Django model, it is possible
to simply extend it with your custom model. When doing this, you effectively
adding your custom model to **whole Ella machinery** and all publishing-related
stuff is ready for you out-of-the box!

Let's have a look at real-world example. We will try to create a **publishable
video** that will have YouTube URL as source. We will keep it simple and use 
YouTube's video player to show the video itself.

.. _plugins-custom-boxes:

============
Custom Boxes
============

.. _plugins-adding-new-actions:

=================================
Adding new actions to Publishable
=================================

.. _plugins-related-finders:

===============================
Defining custom related finders
===============================
