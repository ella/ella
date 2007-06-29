from django.template import loader

class Box(object):
    template_name = "articles/box.html"
    def __init__(self, obj, nodelist):
        self.obj = obj
        self.nodelist = nodelist

    def parse_params(self, definition):
        for line in definition.split('\n'):
            yield line.split(':', 1)

    def resolve_params(self, context):
        if hasattr(self, '_params'):
            return
        self._params = dict(self.parse_params(self.nodelist.render(context)))


    def prepare(self, context):
        self.params = self.resolve_params(context)
        self.render = cache_function(self.render, self.get_key())

    #@cache_function
    def render(self):
        template = loader.get_template(self.params.get('template_name', self.template_name))
        c = Context({'object' : self.obj})
        return template.render(c)

    def get_key(self):
        return 'box:%s:%d:%s' % (
                self.obj.__class__.__name__,
                self.obj.id,
                ','.join('%s:%s' % (key, self.params[key]) for key in sorted(self.params.keys()))
)
