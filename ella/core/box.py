from django.template import loader
from django.utils.datastructures import MultiValueDict
from django.utils.encoding import smart_str
from django.db.models import Model
from django.core.cache import cache
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from ella.core.cache.utils import normalize_key, _get_key, KEY_PREFIX
from ella.core.conf import core_settings


class Box(object):
    """
    Base Class that handles the boxing mechanism.
    """
    can_double_render = False
    def __init__(self, obj, box_type, nodelist, template_name=None, model=None):
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


        if not model:
            model = obj.__class__

        self.name = model.__name__.lower()
        self.verbose_name = model.__name__
        self.verbose_name_plural = model.__name__

        self.is_model = issubclass(model, Model)
        if self.is_model:
            self.ct = ContentType.objects.get_for_model(model)

        if hasattr(model, '_meta'):
            self.name = str(model._meta)
            self.verbose_name = model._meta.verbose_name
            self.verbose_name_plural = model._meta.verbose_name_plural

    def resolve_params(self, text):
        " Parse the parameters into a dict. "
        params = MultiValueDict()
        for line in text.split('\n'):
            pair = line.split(':', 1)
            if len(pair) == 2:
                params.appendlist(pair[0].strip(), pair[1].strip())
        return params

    def prepare(self, context):
        """
        Do the pre-processing - render and parse the parameters and
        store them for further use in self.params.
        """
        self.params = {}

        # no params, not even a newline
        if not self.nodelist:
            return

        # just static text, no vars, assume one TextNode
        if not self.nodelist.contains_nontext:
            text = self.nodelist[0].s.strip()

        # vars in params, we have to render
        else:
            context.push()
            context['object'] = self.obj
            text = self.nodelist.render(context)
            context.pop()

        if text:
            self.params = self.resolve_params(text)

        # override the default template from the parameters
        if 'template_name' in self.params:
            self.template_name = self.params['template_name']

    def get_context(self):
        " Get context to render the template. "
        return {
                'content_type_name' : str(self.name),
                'content_type_verbose_name' : self.verbose_name,
                'content_type_verbose_name_plural' : self.verbose_name_plural,
                'object' : self.obj,
                'box' : self,
        }

    def render(self, context):
        self.prepare(context)
        " Cached wrapper around self._render(). "
        if getattr(settings, 'DOUBLE_RENDER', False) and self.can_double_render:
            if 'SECOND_RENDER' not in context:
                return self.double_render()
        key = self.get_cache_key()
        if key:
            rend = cache.get(key)
            if rend is None:
                rend = self._render(context)
                cache.set(key, rend, core_settings.CACHE_TIMEOUT)
        else:
            rend = self._render(context)
        return rend

    def double_render(self):
        return '''{%% box %(box_type)s for %(name)s with pk %(pk)s %%}%(params)s{%% endbox %%}''' % {
                'box_type' : self.box_type,
                'name' : self.name,
                'pk' : self.obj.pk,
                'params' : '\n'.join(('%s:%s' % item for item in self.params.items())),
        }

    def _get_template_list(self):
        " Get the hierarchy of templates belonging to the object/box_type given. "
        t_list = []
        if hasattr(self.obj, 'category_id') and self.obj.category_id:
            cat = self.obj.category
            base_path = 'box/category/%s/content_type/%s/' % (cat.path, self.name)
            if hasattr(self.obj, 'slug'):
                t_list.append(base_path + '%s/%s.html' % (self.obj.slug, self.box_type,))
            t_list.append(base_path + '%s.html' % (self.box_type,))
            t_list.append(base_path + 'box.html')

        base_path = 'box/content_type/%s/' % self.name
        if hasattr(self.obj, 'slug'):
            t_list.append(base_path + '%s/%s.html' % (self.obj.slug, self.box_type,))
        t_list.append(base_path + '%s.html' % (self.box_type,))
        t_list.append(base_path + 'box.html')

        t_list.append('box/%s.html' % self.box_type)
        t_list.append('box/box.html')

        return t_list

    def _render(self, context):
        " The main function that takes care of the rendering. "
        if self.template_name:
            t = loader.get_template(self.template_name)
        else:
            t_list = self._get_template_list()
            t = loader.select_template(t_list)

        context.update(self.get_context())
        resp = t.render(context)
        context.pop()
        return resp

    def get_cache_key(self):
        " Return a cache key constructed from the box's parameters. "
        if not self.is_model:
            return None

        pars = ''
        if self.params:
            pars = ','.join(':'.join((smart_str(key), smart_str(self.params[key]))) for key in sorted(self.params.keys()))

        return normalize_key('%s:box:%d:%s:%s' % (
                _get_key(KEY_PREFIX, self.ct, pk=self.obj.pk), settings.SITE_ID, str(self.box_type), pars
            ))

