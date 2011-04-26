"""
Customized FilterSpecs.
"""
import logging

from django.utils.translation import ugettext as _
from django.contrib.admin import filterspecs
from django.contrib.sites.models import Site
import django.db

from ella.core.models import Category
from ella.newman.permission import permission_filtered_model_qs

log = logging.getLogger('ella.newman')

class CommonFilter(filterspecs.FilterSpec):
    def __init__(self, f, request, params, model, model_admin, field_path=None):
        self.state = 0
        self.params = params
        self.model = model
        self.links = []
        self.model_admin = model_admin
        self.user = request.user
        #self.lookup_val = request.GET.get(self.lookup_kwarg, None) #selected filter value (not label)
        self.lookup_kwarg = 'NOT SET'
        self.f = f
        self.request_get = request.GET
        if self.f:
            # funny conditional parent constructor call
            super(CommonFilter, self).__init__(f, request, params, model, model_admin)
        self.request_path_info = request.path_info
        self.title_text = ''
        if self.f:
            self.title_text = self.f.verbose_name
        self.active_filter_lookup = None
        self.selected_item = None
        self.remove_from_querystring = []  # may be used as list of keys to be removed from querystring when outputting links

    def get_lookup_kwarg(self):
        """
        this method can be specified as second argument in @filter_spec decorator. (see below)

        If more than one GET parameter is used to filter queryset,
        get_lookup_kwarg() should return list containing these parameters
        (suitable esp. for calendar/date filters etc.).
        """
        return self.lookup_kwarg

    def get_active(self, request_params):
        if self.active_filter_lookup is not None: # cached result
            return self.active_filter_lookup
        self.active_filter_lookup = []
        lookup_multi = 0
        lookup = self.get_lookup_kwarg()
        if type(lookup) == list:
            lookup_multi = len(lookup)
            found = 0
        for p in request_params:
            if not lookup_multi and p == lookup:
                self.active_filter_lookup = [lookup]
                break
            elif lookup_multi:
                if p in lookup:
                    found += 1
                if found == lookup_multi:
                    self.active_filter_lookup = lookup
                    break
        return self.active_filter_lookup

    def is_selected_item(self):
        """
        Returns empty dict if no filter item is selected.
        Otherwise returns dict containing GET params as keys and corresponding
        values.
        """
        active = self.get_active(self.request_get)
        out = dict()
        for par in active:
            if par in self.request_get:
                out[par] = self.request_get[par]
        return out

    def generate_choice(self, **lookup_kwargs):
        """ 
        Returns representation of one choice. 
        Suitable when rendering of all choices isn't necessary. Faster than get_selected() method.
        """
        model = self.model
        lookup = dict()
        if 'field' in self.__dict__:
            if self.field and type(self.field) == django.db.models.fields.related.ForeignKey:
                model = self.field.rel.to
                for key in lookup_kwargs:
                    index  = key.find('__')
                    if index != key.rfind('__'): #multiple __ present
                        modified_key = key[index + 2:]
                        lookup[modified_key] = lookup_kwargs[key]
                    else:
                        lookup[key] = lookup_kwargs[key]

        if len(lookup.keys()) == 0:
            return None
        try:
            thing = model.objects.get(**lookup)
        except (self.model.MultipleObjectsReturned, self.model.DoesNotExist):
            return None
        return thing.__unicode__()

    def get_selected(self):
        " Should be used within a template to get selected item in filter. "
        if hasattr(self, 'selected_item'):
            return self.selected_item
        if not hasattr(self, 'all_choices'):
            # return the same structure with error key set
            return {
                'selected': False,
                'query_string':'',
                'display': '',
                'error': 'TOO EARLY'
            }
        for item in self.all_choices:
            if item['selected']:
                self.selected_item = item
                return item



class CustomFilterSpec(CommonFilter):
    """ custom defined FilterSpec """
    def __init__(self, f, request, params, model, model_admin, field_path=None):
        self.state = 0
        self.params = params
        self.model = model
        self.links = []
        self.model_admin = model_admin
        self.user = request.user
        #self.lookup_val = request.GET.get(self.lookup_kwarg, None) #selected filter value (not label)
        self.lookup_kwarg = 'NOT SET'
        self.f = f
        self.request_get = request.GET
        if self.f:
            # funny conditional parent constructor call
            super(CustomFilterSpec, self).__init__(f, request, params, model, model_admin)
        self.request_path_info = request.path_info
        self.title_text = ''
        if self.f:
            self.title_text = self.f.verbose_name
        self.active_filter_lookup = None
        self.all_choices = []
        self.selected_item = None
        self.remove_from_querystring = []  # may be used as list of keys to be removed from querystring when outputting links

    def filter_func(self):
        raise NotImplementedError('filter_func() method should be overloaded (substituted at run-time).')

    def title(self):
        return self.title_text

    def filter_active(self):
        " Can be used from template. "
        return self.is_active(self.request_get)

    def is_active(self, request_params):
        """
        Returns True if filter is applied, otherwise returns False.
        Tries to find its argument(s) in request querystring.
        """
        return len(self.get_active(request_params)) > 0

    def get_disabled_params(self):
        " Returns parameter dict for constructing HREF to disable this filter. "
        out = dict()
        for key in self.request_get:
            if key in self.get_active(self.request_get):
                continue
            out[key] = self.request_get[key]
        return out

    def generate_choices(self, cl):
        def make_unicode_params(pdict):
            " param values converted to unicode are needed to make dict to dict parameter comparison. "
            out = dict()
            for key in pdict:
                out[key] = unicode(pdict[key])
            return out

        if self.filter_func():
            self.state = 1
        if self.state <= 0:
            yield dict()
        lookup = self.get_lookup_kwarg()
        selected = self.is_selected_item()
        # Reset filter button/a href
        all_query_string = cl.get_query_string(None, self.get_active(self.request_get))
        if all_query_string.endswith('?') and len(all_query_string) == 1:
            all_query_string = '?q='
        yield {'selected': len(selected.keys()) == 0,
               'query_string': all_query_string,
               'display': _('All')}
        for title, param_dict in self.links:
            params = make_unicode_params(param_dict)
            yield {'selected': selected == params,
                   'query_string': cl.get_query_string(param_dict, self.remove_from_querystring),
                   'display': title}

    def get_selected(self):
        " Should be used within a template to get selected item in filter. "
        if self.selected_item:
            return self.selected_item
        if not self.all_choices:
            # return the same structure with error key set
            return {
                'selected': False,
                'query_string':'',
                'display': '',
                'error': 'TOO EARLY'
            }
        for item in self.all_choices:
            if item['selected']:
                self.selected_item = item
                return item

    def choices(self, cl):
        if not self.all_choices:
            self.all_choices = map(None, self.generate_choices(cl))
        return self.all_choices


def filterspec_preregister(cls, test, factory):
    """ method inserts FilterSpec and test to the beginning of FilterSpec registration table """
    cls.filter_specs.insert(0, (test, factory))

def filterspec_clean_all(cls):
    while cls.filter_specs:
        cls.filter_specs.pop()

# Adding class method register_insert() to FilterSpec.
# important is to run following code before admin.py
filterspecs.FilterSpec.register_insert = classmethod(filterspec_preregister)
filterspecs.FilterSpec.clean_registrations = classmethod(filterspec_clean_all)


def filter_spec(field_test_func, lookup_kwarg_func=None, title=None):
    """
    Decorator ``filter_spec`` creates custom filter.

    Example:
    @filter_spec(lambda field_to_test: isinstance(field_to_test, models.DateField))
    @filter_spec(lambda field_to_test: isinstance(field_to_test, models.DateField), lambda p: 'category__exact')
    """
    def decorate(filter_func):
        name = '%s_%s' % (filter_func.__name__, CustomFilterSpec.__name__)
        cls = type(name, (CustomFilterSpec,), {})
        cls.filter_func = filter_func
        if lookup_kwarg_func:
            cls.get_lookup_kwarg = lookup_kwarg_func
        if title:
            cls.title = lambda fspec: title
        filterspecs.FilterSpec.register_insert(field_test_func, cls)
        return filter_func
    return decorate

class NewmanSiteFilter(CustomFilterSpec):
    " Site customized filter. Filtering is done via Site.category_set()... "
    site_field_path = 'category__site__id__exact'

    def title(self):
        return _('Site')

    def get_lookup_kwarg(self):
        for param in self.request_get:
            if param.startswith(self.site_field_path):
                self.selected_lookup = param
                return param
        return ''

    def filter_func(fspec):
        root_cats = Category.objects.filter(tree_parent__isnull=True)
        qs = permission_filtered_model_qs(root_cats, fspec.user)
        for cat in qs:
            lookup_dict = dict()
            lookup_dict[fspec.site_field_path] = cat.site.pk
            link_text = '%s (%s)' % (cat.site.name, cat.site.domain)
            link = (link_text, lookup_dict)
            fspec.links.append(link)
        return True

    def generate_choice(self, **lookup_kwargs):
        category_id = lookup_kwargs.get(self.site_field_path, '')
        if not category_id or not category_id.isdigit():
            return None
        try:
            thing = Site.objects.get( pk=int(category_id) )
        except (Site.MultipleObjectsReturned, Site.DoesNotExist):
            return None
        return thing.__unicode__()

# -------------------------------------
# Standard django.admin filters
# -------------------------------------

class FilterSpecEnhancement(CommonFilter):
    def filter_active(self):
        " Can be used from template. "
        return self.is_active(self.params)

class RelatedFilterSpec(filterspecs.RelatedFilterSpec, FilterSpecEnhancement):
    def is_active(self, request_params):
        """
        Returns True if filter is applied, otherwise returns False.
        Tries to find its argument(s) in request querystring.
        """
        return self.lookup_kwarg in request_params

    def choices(self, cl):
        if not hasattr(self, 'all_choices'):
            c = super(RelatedFilterSpec, self).choices(cl)
            self.all_choices = map(None, c)
        return self.all_choices

filterspecs.FilterSpec.register_insert(lambda f: bool(f.rel), RelatedFilterSpec)

class ChoicesFilterSpec(filterspecs.ChoicesFilterSpec, FilterSpecEnhancement):
    def is_active(self, request_params):
        return self.lookup_kwarg in request_params

filterspecs.FilterSpec.register_insert(lambda f: bool(f.choices), ChoicesFilterSpec)

class DateFieldFilterSpec(filterspecs.DateFieldFilterSpec, FilterSpecEnhancement):
    def __init__(self, *args, **kwargs):
        super(DateFieldFilterSpec, self).__init__(*args, **kwargs)
        self.active_choice = None

    def get_lookup_kwarg(self):
        out = []
        for title, param_dict in self.links:
            for key in param_dict:
                out.append(key)
        return out

    def is_active(self, request_params):
        if self.__get_active_choice() is None:
            return False
        return True

    def get_active(self, request_params):
        if self.active_filter_lookup is not None: # cached result
            return self.active_filter_lookup
        self.active_filter_lookup = []
        lookup_multi = 0
        lookup = self.get_lookup_kwarg()
        if type(lookup) == list:
            lookup_multi = len(lookup)
            found = 0
        for p in request_params:
            if not lookup_multi and p == lookup:
                self.active_filter_lookup = [lookup]
                break
            elif lookup_multi:
                if p in lookup:
                    found += 1
                    self.active_filter_lookup.append(p)
        return self.active_filter_lookup

    def __get_active_choice(self):
        if self.active_choice is not None:
            return self.active_choice
        for title, param_dict in self.links:
            if param_dict and self.date_params == param_dict:
                self.active_choice = (title, param_dict)
                return self.active_choice

    def generate_choice(self, **lookup_kwargs):
        active_title, active_param_dict = self.active_choice
        if lookup_kwargs == active_param_dict:
            return active_title
        for title, param_dict in self.links:
            if lookup_kwargs == param_dict:
                return self.active_choice
        return None

filterspecs.FilterSpec.register_insert(lambda f: isinstance(f, models.DateField), DateFieldFilterSpec)


class BooleanFieldFilterSpec(filterspecs.BooleanFieldFilterSpec, FilterSpecEnhancement):
    def is_active(self, request_params):
        return False

filterspecs.FilterSpec.register_insert(lambda f: isinstance(f, models.BooleanField), BooleanFieldFilterSpec)

from django.db import models
filterspecs.FilterSpec.register_insert(lambda f: isinstance(f, models.BooleanField) or isinstance(f, models.NullBooleanField), BooleanFieldFilterSpec)
