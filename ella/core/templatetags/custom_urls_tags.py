"""
Lot of what you see here has been stolen from django's {% url %} tag
"""
from django.core.urlresolvers import NoReverseMatch
from django.template import Node, TemplateSyntaxError, Library
from django.utils.encoding import smart_str

from ella.core import custom_urls

register = Library()

class CustomURLNode(Node):
    def __init__(self, obj, view_name, args, kwargs, asvar):
        self.obj = obj
        self.view_name = view_name
        self.args = args
        self.kwargs = kwargs
        self.asvar = asvar
      
    def render(self, context):
        args = [arg.resolve(context) for arg in self.args]
        kwargs = dict([(smart_str(k,'ascii'), v.resolve(context))
                       for k, v in self.kwargs.items()])
        obj = self.obj.resolve(context)
      
        url = ''
        try:
            url = custom_urls.resolver.reverse(obj, self.view_name, *args, **kwargs)
        except NoReverseMatch, e:
            if self.asvar is None:
                raise e
      
        if self.asvar:
            context[self.asvar] = url
            return ''
        else:
            return url

@register.tag
def custom_url(parser, token):
    bits = token.split_contents()
    if len(bits) < 3: 
        raise TemplateSyntaxError("'%s' takes at least one argument"
                                  " (path to a view)" % bits[0])
    obj = parser.compile_filter(bits[1])
    viewname = bits[2]
    args = []
    kwargs = {}
    asvar = None
 
    if len(bits) > 3:
        bits = iter(bits[3:])
        for bit in bits:
            if bit == 'as':
                asvar = bits.next()
                break
            else:
                for arg in bit.split(","):
                    if '=' in arg:
                        k, v = arg.split('=', 1)
                        k = k.strip()
                        kwargs[k] = parser.compile_filter(v)
                    elif arg:
                        args.append(parser.compile_filter(arg))
    return CustomURLNode(obj, viewname, args, kwargs, asvar)
