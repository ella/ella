.. _plugins-custom-boxes:

Custom Boxes
************

We have defined our new publishable object, but something still remains a
little unclear: **how to embed the video in the HTML page**. In this part of
walkthrough, we will present you a way that is preferred when working with
Ella. These are so-called **boxes**.

As described in :ref:`tutorial-boxes`, boxes are something you can call
an *include on steroids*. Boxes behave very much like standard Django
``{% include %}`` templatetag, but are suited to be used with publishable
objects. They do following things for you so you don't need to care about
them:

* Template path resolution
* Object-specific context within the included template
* Ability to accept advanced parameters

Now back to the ``Video`` publishable subclass. What we want to achieve is
that our ``Video`` is being rendered in the page. For this, we will create a
custom ``Box`` subclass. Here is, how a desired result will look when embedding
the video in the page:

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

Note the ``get_context`` method. Since ``width`` and ``height`` parameters are
specific to our ``VideoBox`` and not recognized by other boxes, we need to
handle them and pass them **into the include context**. ``self.params`` is a
dictionary holding parameters used to call the box. We provide sane defaults
when the parameters are not provided so that we can still call the box by using
simple ``{% box video_player for video_object %}{% endbox %}``.

Next step is to let Ella know, that we want a **special type** of box to be
used with our ``Video``. If we didn't do that, Ella would use a basic ``Box``
class which is missing the ``width`` and ``height`` parameters. To tie our
model with the ``VideoBox`` set the ``box_class`` class variable on the
``Video`` model::

    class Video(Publishable):
        ...
        box_class = VideoBox
        ...
        
In order to actually render something we also need to create a HTML template.
Box templates are placed in ``box`` directory within paths where Django template
finders are **able to reach them** (if you are unsure what a template finder
is, please refer to the `Docs`_). The name of the box also serves as name of
the template to use. In our case, the name of the box is ``video_player`` so
the template name is going to be ``video_player.html``. Boxes provide a
template search fallback which we're not gonna discuss here to keep the thing
simple. For further information, see :ref:`reference-templatetags`. 

Our box is fairly simple. We are gonna use the code provided by YouTube and it
will look like this:

.. code-block:: html+django

    <!-- in templates/box/video_player.html -->
    <iframe width="{{ width }}" height="{{ height }}" src="http://www.youtube.com/embed/{{ object.code }}" frameborder="0" allowfullscreen></iframe>
    
See how nicely box integrates all things we have so far together. It uses
``object.code`` to build up the URL and ``width`` and ``height`` attributes to
define the video player dimensions.

.. _Docs: https://docs.djangoproject.com/en/dev/ref/templates/api/#loading-templates




