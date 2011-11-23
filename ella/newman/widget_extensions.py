'''
Created on 3.11.2011

@author: xaralis
'''
from ella.newman.conf import newman_settings

__all__ = ['rich_text_extensions',]

JS_EXTENSIONS = []
CSS_EXTENSIONS = []

class NewmanRichTextAreaExtensions(object):
    """
    Singleton object to keep track of RichTextArea extensions for markdown.
    """
    
    def register(self, path, type='js'):
        """
        Add JS extension path to load for RichTextArea
        """
        if not type in ('js', 'css'):
            raise ValueError('Only js or css types are supported.')
        if type == 'js':
            JS_EXTENSIONS.append(path)
        else:
            CSS_EXTENSIONS.append(path)
            
    def unregister(self, path, type):
        """
        Remove previously added JS extension path to load for RichTextArea
        """
        if not type in ('js', 'css'):
            raise ValueError('Only js or css types are supported.')
        if type == 'js':
            if path in self.js_extensions:
                JS_EXTENSIONS.remove(path)
        else:
            if path in self.css_extensions:
                CSS_EXTENSIONS.remove(path)
            
    def get_js_extensions(self):
        """
        Get list of all JS extension paths
        """
        return JS_EXTENSIONS
    
    def get_css_extensions(self):
        """
        Get list of all CSS extension paths
        """
        return CSS_EXTENSIONS


rich_text_extensions = NewmanRichTextAreaExtensions()

use_markdown = False
try:
    import markdown2 as m
    use_markdown = True
except ImportError:
    try:
        import markdown as m
        use_markdown = True
    except ImportError:
        pass
    
if use_markdown:
    import inspect
    arguments = inspect.getargspec(getattr(m, 'markdown'))[0]
    extension_js = None 
    if 'extensions' in arguments:
        extension_js = 'js/fuckitup_extensions/markdown_extensions_tables.js'
    if 'extras' in arguments:
        extension_js = 'js/fuckitup_extensions/markdown_extras_tables.js'
    if extension_js is not None:    
        rich_text_extensions.register(
                newman_settings.MEDIA_PREFIX + extension_js,
                type='js'
            )
        rich_text_extensions.register(
            newman_settings.MEDIA_PREFIX + 'css/fuckitup_extensions/markdown_tables.css',
            type='css'
        )
    
