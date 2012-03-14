.. _plugins-overriding-publishable-urls:

Overriding Publishable URLs
###########################

Adding custom actions
*********************

Consider a situation, when we would like to have discussion about the video on
a separate page while **keeping the nice URL** prefix Ella creates for it's
publishable objects. There is a simple solution for that. Ella's custom URL
resolver allows us to **add actions** for the Publishable objects easily.

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

When registering custom URLs, we use ``ella.core.custom_urls.resolver`` instead
of regular Django url machinery. This does a little Python magic so that your
URLs will be appended to base Publishable URL. Note the use of ``model``
argument in ::

    resolver.register(urlpatterns, model=Video)
    
This means, that the custom action will be available only for a ``Video`` model.
If we wanted to add our *discussion action* to all Publishable models, we would
simply omit the ``model`` argument altogether.

As you have probably noticed, we are using ``show_discussion`` view function
without declaring it, let's fix that up::

    # in yourapp/video/views.py
    
    def show_discussion(request, context):
        obj = context['object']
        return render('yourapp/discussion.html', {'object': obj})

Views that are used with Ella's resolver always accept ``request`` (which is a
normal Django request object) and ``context`` which is a dictionary that
contains following data:

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
**************************

Besides custom actions, it is also possible to completely override the view
which handles rendering of object detail page. Such a requirement might occur
in these situations:

* You need to add custom object-related data to the **context** in the detail
  template.
* You wish to change the way the view itself **works**. This can be used for
  advanced behavior changes which are needed only rarely.

To define a custom view, we will use the Ella's URL resolver again::

    # in your urls.py
    from django.conf.urls.defaults import patterns, url

    from ella.core.custom_urls import resolver

    from yourapp.models import Video    
    from yourapp.views import video_detail

    resolver.register_custom_detail(Video, article_detail)    

This will result in calling our ``article_detail`` view instead of the default
one. Custom detail views are called with same arguments as custom action views.
For reference, see the table with custom view arguments above. For further information
on Ella's ``ObjectDetailView``, see :ref:`reference-views`.

