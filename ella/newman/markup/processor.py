# TODO: Where we will define output format? (HTML4/5/XHTML/...)

def markdown(src, **kwargs):
    try:
        from markdown2 import markdown as m
    except ImportError:
        from markdown import markdown as m

    return m(src) #, html4tags, tab_width, safe_mode, extras, link_patterns, use_file_vars)

def czechtile(src, **kwargs):
    pass
