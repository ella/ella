.. _markdown:

========
Markdown
========

You can use `django-markup <https://github.com/ella/django-markup>`_ to allow for more expressive contents of articles, descriptions etc. This way, your editors won't need to use HTML to write articles. Ella adds wrapper around django-markup that allows you to chose default :class:`TextProcessor` type to use. By defaults, it is set like this::

        DEFAULT_MARKUP = 'markdown'

This means that Ella will use markdown as default renderer. There are more choices depending of what you prefer: textile, reStructuredText etc. Ella works out of the box with markdown/markdown2 in default settings - the same as django-markup does. This requires one of following markdown implementations to be installed:

* `Python-Markdown <https://github.com/waylan/Python-Markdown>`_
* `python-markdown2 <https://github.com/trentm/python-markdown2>`_

For further details about django-markup settings, please refer to it's own `documentation page <https://github.com/ella/django-markup/blob/master/docs/source/index.rst>`_.

Tables in markdown
------------------

If you need to use tables, install Python-Markdown. Moreover, make sure your settings contain following piece of code::

        DEFAULT_MARKUP = 'markdown'
        MARKUP_MARKDOWN_EXTENSIONS = ['tables']
