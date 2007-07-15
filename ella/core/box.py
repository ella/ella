from django.template import loader, Context

BOX_INFO = 'ella.core.box.BOX_INFO'
class Box(object):
    """
    Base Class
    """
    def __init__(self, obj, box_type, nodelist, template_name=None):
        self.obj = obj
        self.box_type = box_type
        self.nodelist = nodelist
        self.template_name = template_name or 'box/%s.%s/%s.html' % (obj._meta.app_label, obj._meta.module_name, box_type)

    def parse_params(self, definition):
        for line in definition.split('\n'):
            pair = line.split(':', 1)
            if len(pair) == 2:
                yield (pair[0].strip(), pair[1].strip())
            else:
                pass
                # TODO log warning

    def resolve_params(self, context):
        return dict(self.parse_params(self.nodelist.render(context)))

    def prepare(self, context):
        context.push()
        context['object'] = self.obj
        self.params = self.resolve_params(context)
        context.pop()
        # TODO add caching
        #self.render = cache_function(self.render, self.get_key())

    #@cache_function
    def render(self):
        template = loader.get_template(self.params.get('template_name', self.template_name))
        c = Context({'object' : self.obj})
        return template.render(c)

    def get_cache_key(self):
        return 'ella.core.box.Box.render:%s:%s:%s:%s' % (
                self.obj.__class__.__name__,
                self.box_type,
                self.obj._get_pk_val(),
                ','.join('%s:%s' % (key, self.params[key]) for key in sorted(self.params.keys()))
)
