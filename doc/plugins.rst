.. _plugins:

Plugins
#######

Ella tries to keep the core framework **as lightweight as possible**. This has very good reasons:

* it let's what is required for your app to **your decision**
* it minimizes the **dependencies** of core application
* it makes the development faster, because you can enhance your module while not needing to update the rest of the code
  
Because of this philosophy, **plugins** were introduced in version **3.0.0**.

Basic plugin structure
**********************

All Ella plugins come as Django applications bundled using setuptools. Each plugin has dependency on the Ella's core, so Ella is always required and plugins can hardly be used without it.

As Ella provides significant flexibility, plugins are able to do quite a lot of magic, like following:

* Define custom ``Publishable`` objects via subclassing. For more details, see :ref:`plugins-subclassing-publishable`.
* Extend actions performed over the ``Publishable`` objects, for details, see :ref:`plugins-overriding-publishable-urls` section.
* Create custom ``Box`` classess for fine-tuned includes. This is discussed in detail in section :ref:`plugins-custom-boxes`.

.. _plugins-subclassing-publishable:

Subclassing Publishable
***********************

Due to the fact that ``Publishable`` is common Django model, it is possible to simply extend it with your custom model. When doing this, you effectively adding your custom model to **whole Ella machinery** and all publishing-related stuff is ready for you out-of-the box!

Let's have a look at real-world example. During this walkthrough, we will try to create a **publishable video** that will have YouTube *video code* as source. We will keep it simple and use YouTube's video player to show the video itself.

The very first step is to create your own application using the standard Django way:

.. code-block:: bash

    django-admin.py startapp video

After creating the app to hold it, let's define the class itself. If you are acustomed to Django models, this is going to look very familiar to you.::
   
    # in models.py within your video application
    
    from django.db import models
    from django.utils.translation import ugettext_lazy as _
    
    from ella.core.models import Publishable
    
    class YoutubeVideo(Publishable):
        code = models.CharField(max_length=20, title=_('Code'))
        
        class Meta:
            verbose_name = _('Youtube video')
            verbose_name_plural = _('Youtube videos')
        
        def __unicode__(self):
            return self.code      
            
.. note::
    If you want to examine whats is going on behind the scenes when subclassing
    Django models, have a look at `Django model inheritance`_. We are using 
    Multi-table inheritance so that each ``Publishable`` subclass has a hidden
    pointer - ``publishable_ptr`` - to the ``Publishable`` object. This pointer
    also acts as PK in the DB table.

Next step is to put the new app to the settings.::

    INSTALLED_APPS = (
        'ella.core',
        'ella.articles',
        ...
        'yourproject.video',
    )
    
Finally, resync your database so the DB table for the class is created:

.. code-block:: bash

    django-admin.py syncdb
    
By defining this, we already have a working publishable object, nothing more is needed. Of course, in real world, you would probably need to do some polishing (adding better title, etc.), but for now, this is enough. 

.. _Django model inheritance: https://docs.djangoproject.com/en/dev/topics/db/models/#model-inheritance

.. _plugins-custom-boxes:

Custom Boxes
************

We have defined our new publishable object, but something still remains a little unclear: **how to embed the video in the HTML page**. In this part of walkthrough, we will present you a way that is preferred when working with Ella. These are so-called **boxes**.

As described in :ref:`tutorial-boxes`, boxes are something you can call an *include on steroids*. Boxes behave very much like standard Django ``{% include %}`` templatetag, but are suited to be used with publishable objects. They do following things for you so you don't need to care about them:

* Template path resolution
* Object-specific context within the included template
* Ability to accept advanced parameters

Now back to the ``Video`` publishable subclass. What we want to achieve is that our ``Video`` is being rendered in the page. For this, we will create a custom ``Box`` subclass. Here is, how a desired result will look when embedding the video in the page:

.. code-block:: html+django

    <h1>Watch the video right here!</h1>
    
    {% box video_player for video_object %}
        width: 400
        height: 200
    {% endbox %}
    
The first thing you need to do is to define the box sublcass itself::
    
    # in models.py
    from ella.core.box import Box

    class VideoBox(Box):
        def get_context(self):
            context = super(VideoBox, self).get_context()
            context.update({
                'width': self.params.get('width', '400'),
                'height': self.params.get('height', '200')
            })
            return context

Note the ``get_context`` method. Since ``width`` and ``height`` parameters are specific to our ``VideoBox`` and not recognized by other boxes, we need to handle them and pass them **into the include context**. ``self.params`` is a dictionary holding parameters used to call the box. We provide sane defaults when the parameters are not provided so that we can still call the box by using simple ``{% box video_player for video_object %}{% endbox %}``.

Next step is to let Ella know, that we want a **special type** of box to be used with our ``Video``. If we didn't do that, Ella would use a basic ``Box`` class which is missing the ``width`` and ``height`` parameters. To tie our model with the ``VideoBox`` set the ``box_class`` class variable on the ``Video`` model::

    class Video(Publishable):
        ...
        box_class = VideoBox
        ...
        
In order to actually render something we also need to create a HTML template. Box templates are placed in ``box`` directory within paths where Django template finders are **able to reach them** (if you are unsure what a template finder is, please refer to the `Docs`_). The name of the box also serves as name of the template to use. In our case, the name of the box is ``video_player`` so the template name is going to be ``video_player.html``. Boxes provide a template search fallback which we're not gonna discuss here to keep the thing simple. For further information, see :ref:`core-templatetags`. 

Our box is fairly simple. We are gonna use the code provided by YouTube and it will look like this:

.. code-block:: html+django

    <!-- in templates/box/video_player.html -->
    <iframe width="{{ width }}" height="{{ height }}" src="http://www.youtube.com/embed/{{ object.code }}" frameborder="0" allowfullscreen></iframe>
    
See how nicely box integrates all things we have so far together. It uses ``object.code`` to build up the URL and ``width`` and ``height`` attributes to define the video player dimensions.

.. _Docs: https://docs.djangoproject.com/en/dev/ref/templates/api/#loading-templates

.. _plugins-overriding-publishable-urls:

Overriding Publishable URLs
***************************

Adding custom actions
=====================

Consider a situation, when we would like to have discussion about the video on a separate page while **keeping the nice URL** prefix Ella creates for it's publishable objects. There is a simple solution for that. Ella's custom URL resolver allows us to **add actions** for the Publishable objects easily.

We would like our URL to have following form::

    /about/2007/08/11/videos/ella-first-in-production/discussion/
    
To do this, we will append a custom view function for the ``Video`` model::

    # in yourapp/video/urls.py
    from django.conf.urls.defaults import url, patterns
    
    from ella.core.custom_urls import resolver

    from yourapp.models import Video    
    from yourapp.video.views import show_discussion
    
    urlpatterns = patterns('',
        url(r'^discussion/$', show_discussion, name='video-show-discussions'),
    )
    
    resolver.register(urlpatterns, model=Video)

When registering custom URLs, we use ``ella.core.custom_urls.resolver`` instead of regular Django url machinery. This does a little Python magic so that your URLs will be appended to base Publishable URL. Note the use of ``model`` argument in ::

    resolver.register(urlpatterns, model=Video)
    
This means, that the custom action will be available only for a ``Video`` model. If we wanted to add our *discussion action* to all Publishable models, we would simply omit the ``model`` argument altogether.

As you have probably noticed, we are using ``show_discussion`` view function without declaring it, let's fix that up::

    # in yourapp/video/views.py
    
    def show_discussion(request, context):
        obj = context['object']
        return render('yourapp/discussion.html', {'object': obj})

Views that are used with Ella's resolver always accept ``request`` (which is a normal Django request object) and ``context`` which is a dictionary that contains following data:

.. _plugins-custom-view-aguments:

.. table:: Custom view arguments

    ==================================  ================================================
    Key                                 Value
    ==================================  ================================================
    ``object``                          The publishable object itself.
    ``category``                        ``Category`` object related to the URL.
    ``content_type_name``               Verbose name of Content type of the Publishable
                                        (e.g. Article, Video and so on).
    ``content_type``                    ``ContentType`` instance for Publishable.
    ==================================  ================================================

Overriding objects' detail
==========================

Besides custom actions, it is also possible to completely override the view which handles rendering of object detail page. Such a requirement might occur in these situations:

* You need to add custom object-related data to the **context** in the detail template.
* You wish to change the way the view itself **works**. This can be used for advanced behavior changes which are needed only rarely.

To define a custom view, we will use the Ella's URL resolver again::

    # in your urls.py
    from django.conf.urls.defaults import patterns, url

    from ella.core.custom_urls import resolver

    from yourapp.models import Video    
    from yourapp.views import video_detail

    resolver.register_custom_detail(Video, article_detail)    

This will result in calling our ``article_detail`` view instead of the default one. Custom detail views are called with same arguments as custom action views. For reference, see :ref:`plugins-custom-view-arguments`. For further information on Ella's ``ObjectDetailView``, see :ref:`core-views`.

