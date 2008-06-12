from django.template import loader
from django.utils.datastructures import MultiValueDict
from django.utils.encoding import smart_str
from django.core.cache import cache
from django.conf import settings

from ella.core.cache.invalidate import CACHE_DELETER
from ella.core.cache.template_loader import select_template
from ella.core.cache.utils import normalize_key


BOX_INFO = 'ella.core.box.BOX_INFO'
MEDIA_KEY = 'ella.core.box.MEDIA_KEY'


class Box(object):
    """
    Base Class that handles the boxing mechanism.
    """
    js = []
    css = []
    can_double_render = False
    def __init__(self, obj, box_type, nodelist, template_name=None):
        """
        Params:

            obj - target object
            box_type - box name
            nodelist - contents of the pair tag
            template_name - override the template
        """
        self.obj = obj
        self.box_type = box_type
        self.nodelist = nodelist
        self.template_name = template_name

    def parse_params(self, definition):
        " A helper function to parse the parameters inside the box tag. "
        for line in definition.split('\n'):
            pair = line.split(':', 1)
            if len(pair) == 2:
                yield (pair[0].strip(), pair[1].strip())
            else:
                pass
                # TODO log warning

    def resolve_params(self, context):
        " Parse the parameters into a dict. "
        params = MultiValueDict()
        for key, value in self.parse_params(self.nodelist.render(context)):
            params.appendlist(key, value)
        return params

    def prepare(self, context):
        """
        Do the pre-processing - render and parse the parameters and
        store them for further use in self.params.
        """
        context.push()
        context['object'] = self.obj
        self.params = self.resolve_params(context)
        context.pop()
        self._context = context

    def get_context(self):
        " Get context to render the template. "
        if 'level' in self.params and self.params['level'].isdigit():
            level = int(self.params['level'])
        else:
            level = 1

        return {
                'content_type_name' : '.'.join((self.obj._meta.app_label, self.obj._meta.module_name)),
                'content_type_verbose_name' : self.obj._meta.verbose_name,
                'content_type_verbose_name_plural' : self.obj._meta.verbose_name_plural,
                'object' : self.obj,
                'level' : level,
                'next_level' : level + 1,
                'css_class' : self.params.get('css_class', ''),
                'name' : self.params.get('name', ''),
                'box' : self,
}

    def get_cache_tests(self):
        " Return tests for ella.core.cache.invalidate "
        from ella.db_templates.models import DbTemplate
        if not DbTemplate._meta.installed:
            return []
        return [ (DbTemplate, 'name:%s' % t) for t in self._get_template_list() ]

    def render(self):
        " Cached wrapper around self._render(). "
        if getattr(settings, 'DOUBLE_RENDER', False) and self.can_double_render:
            if 'SECOND_RENDER' not in self._context:
                return self.double_render()
        key = self.get_cache_key()
        rend = cache.get(key)
        if rend is None:
            rend = self._render()
            cache.set(key, rend, getattr(settings, 'CACHE_TIMEOUT', 20*60))
            for model, test in self.get_cache_tests():
                CACHE_DELETER.register_test(model, test, key)
            CACHE_DELETER.register_pk(self.obj, key)
        return rend

    def double_render(self):
        return '''{%% box %(box_type)s for %(app_label)s.%(module_name)s with pk %(pk)s %%}{%% endbox %%}''' % {
                'box_type' : self.box_type,
                'app_label' : self.obj._meta.app_label,
                'module_name' : self.obj._meta.module_name,
                'pk' : self.obj.pk,
                'params' : '\n'.join(('%s:%s' % item for item in self.params.items()))
}

    def _get_template_list(self):
        " Get the hierarchy of templates belonging to the object/box_type given. "
        t_list = []
        if hasattr(self.obj, 'category_id') and self.obj.category_id:
            from ella.core.models import Category
            from ella.core.cache import get_cached_object
            cat = get_cached_object(Category, pk=self.obj.category_id)
            base_path = 'box/category/%s/content_type/%s.%s/' % (cat.path, self.obj._meta.app_label, self.obj._meta.module_name)
            if hasattr(self.obj, 'slug'):
                t_list.append(base_path + '%s/%s.html' % (self.obj.slug, self.box_type,))
            t_list.append(base_path + '%s.html' % (self.box_type,))
            t_list.append(base_path + 'box.html')

        base_path = 'box/content_type/%s.%s/' % (self.obj._meta.app_label, self.obj._meta.module_name)
        if hasattr(self.obj, 'slug'):
            t_list.append(base_path + '%s/%s.html' % (self.obj.slug, self.box_type,))
        t_list.append(base_path + '%s.html' % (self.box_type,))
        t_list.append(base_path + 'box.html')

        t_list.append('box/%s.html' % self.box_type)
        t_list.append('box/box.html')

        return t_list

    def _render(self):
        " The main function that takes care of the rendering. "
        media = self._context.dicts[-1].setdefault(MEDIA_KEY, {'js' : set([]), 'css' : set([])})
        my_media = self.get_media()
        media['js'] = media['js'].union(my_media['js'])
        media['css'] = media['css'].union(my_media['css'])

        if self.template_name:
            t = loader.get_template(self.template_name)
        else:
            t_list = self._get_template_list()
            t = select_template(t_list)

        self._context.update(self.get_context())
        resp = t.render(self._context)
        self._context.pop()
        return resp

    def get_media(self):
        " Get a list of media files requested by the tag. "
        if u'js' in self.params:
            js = set(self.js + self.params.getlist('js'))
        else:
            js = set(self.js)

        if u'css' in self.params:
            css = set(self.css + self.params.getlist('css'))
        else:
            css = set(self.css)

        return {'js' : js, 'css' : css,}

    def get_cache_key(self):
        " Return a cache key constructed from the box's parameters. "
        if self.params:
            pars = ','.join(':'.join((smart_str(key), smart_str(self.params[key]))) for key in sorted(self.params.keys()))
        else:
            pars = ''
        return normalize_key('ella.core.box.Box.render:%d:%s:%s:%d:%s' % (
                    settings.SITE_ID, self.obj.__class__.__name__, str(self.box_type), self.obj.pk, pars
))

