"""
Customized FilterSpecs.
"""
import logging

from django.utils.encoding import smart_unicode, iri_to_uri
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.contrib.admin.filterspecs import FilterSpec
from django.contrib.admin import filterspecs

from ella.ellaadmin.options import EllaModelAdmin

log = logging.getLogger('ella.newman')


class CustomFilterSpec(FilterSpec):
    """ custom defined FilterSpec """
    def __init__(self, f, request, params, model, model_admin, field_path=None):
        self.state = 0
        self.params = params
        self.model = model
        self.links = []
        self.model_admin = model_admin
        self.field_path = field_path
        self.user = request.user
        #self.lookup_val = request.GET.get(self.lookup_kwarg, None) #selected filter value (not label)
        self.lookup_kwarg = 'NOT SET'
        self.f = f
        self.request_get = request.GET
        super(CustomFilterSpec, self).__init__(f, request, params, model, model_admin, field_path=field_path)
        self.request_path_info = request.path_info
        self.title_text = self.field.verbose_name

    def filter_func(self):
        raise NotImplementedError('filter_func() method should be overloaded (substituted at run-time).')

    def title(self):
        return self.title_text

    def get_lookup_kwarg(self):
        """ 
        this method can be specified as second argument in @filter_spec decorator. (see below)

        If more than one GET parameter is used to filter queryset, 
        get_lookup_kwarg() should return list containing these parameters 
        (suitable esp. for calendar/date filters etc.).
        """
        return self.lookup_kwarg

    def is_active(self, request_params):
        """ 
        Returns True if filter is applied, otherwise returns False.
        Tries to find its argument(s) in request querystring.
        """
        lookup_multi = 0
        lookup = self.get_lookup_kwarg()
        if type(lookup) == list:
            lookup_multi = len(lookup)
            found = 0
        for p in request_params:
            if not lookup_multi and p == lookup:
                return [lookup]
            elif lookup_multi:
                if p in lookup:
                    found += 1
                if found == lookup_multi:
                    return lookup
        return False

    def is_selected_item(self):
        """
        Returns empty dict if no filter item is selected.
        Otherwise returns dict containing GET params as keys and corresponding
        values. 
        """
        active = self.is_active(self.request_get)
        if not active:
            return dict()
        out = dict()
        for par in active:
            if par in self.request_get:
                out[par] = self.request_get[par]
        return out

    def choices(self, cl):
        def make_unicode_params(pdict):
            " param values converted to unicode are needed to make dict to dict parameter comparison. "
            out = dict()
            for key in pdict:
                out[key] = unicode(pdict[key])
            return out

        if self.filter_func():
            self.state = 1
        if self.state > 0:
            lookup = self.get_lookup_kwarg()
            selected = self.is_selected_item()
            for title, param_dict in self.links:
                params = make_unicode_params(param_dict)
                yield {'selected': selected == params,
                       'query_string': cl.get_query_string(param_dict, []),
                       'display': title}


def filterspec_preregister(cls, test, factory):
    """ method inserts FilterSpec and test to the beginning of FilterSpec registration table """
    cls.filter_specs.insert(0, (test, factory))

def filterspec_clean_all(cls):
    while cls.filter_specs:
        cls.filter_specs.pop()

# Adding class method register_insert() to FilterSpec.
# important is to run following code before admin.py
FilterSpec.register_insert = classmethod(filterspec_preregister)
FilterSpec.clean_registrations = classmethod(filterspec_clean_all)


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
        FilterSpec.register_insert(field_test_func, cls)
        return filter_func
    return decorate

# -------------------------------------
# Standard django.admin filters
# -------------------------------------
# TODO register all of them!

class RelatedFilterSpec(filterspecs.RelatedFilterSpec):
    def is_active(self, request_params):
        """ 
        Returns True if filter is applied, otherwise returns False.
        Tries to find its argument(s) in request querystring.
        """
        for p in request_params:
            if p == self.lookup_kwarg:
                return True
        return False

FilterSpec.register_insert(lambda f: bool(f.rel), RelatedFilterSpec)
