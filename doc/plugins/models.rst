.. _plugins-subclassing-publishable:

Subclassing Publishable
#######################

Due to the fact that ``Publishable`` is common Django model, it is possible to
simply extend it with your custom model. When doing this, you effectively adding
your custom model to **whole Ella machinery** and all publishing-related stuff
is ready for you out-of-the box!

Let's have a look at real-world example. During this walkthrough, we will try
to create a **publishable video** that will have YouTube *video code* as source.
We will keep it simple and use YouTube's video player to show the video itself.

The very first step is to create your own application using the standard Django
way:

.. code-block:: bash

    django-admin.py startapp video

After creating the app to hold it, let's define the class itself. If you are
acustomed to Django models, this is going to look very familiar to you.::
   
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
    
By defining this, we already have a working publishable object, nothing more is
needed. Of course, in real world, you would probably need to do some polishing
(adding better title, etc.), but for now, this is enough. 

.. _Django model inheritance: https://docs.djangoproject.com/en/dev/topics/db/models/#model-inheritance


