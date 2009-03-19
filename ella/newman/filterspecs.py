"""
Customized FilterSpecs.
"""
import logging

from django.utils.encoding import smart_unicode, iri_to_uri
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.contrib.admin.filterspecs import FilterSpec

from ella.ellaadmin.options import EllaModelAdmin

log = logging.getLogger('ella.newman.filterspecs')


class CustomFilterSpec(FilterSpec):
    """ custom defined FilterSpec """
    def __init__(self, f, request, params, model, model_admin, field_path=None):
        self.state = 0
        self.params = params
        self.model = model
        self.model_admin = model_admin
        self.field_path = field_path
        super(CustomFilterSpec, self).__init__(f, request, params, model, model_admin, field_path=field_path)
        self.request_path_info = request.path_info

    def filter_func(self):
        raise NotImplementedError('filter_func() method should be overloaded (substituted at run-time).')

    def title(self):
        return self.field.verbose_name

    def choices(self, cl):
        if self.filter_func():
            self.state = 1
        if self.state > 0:
            for title, param_dict in self.links:
                yield {'selected': self.date_params == param_dict,
                       'query_string': cl.get_query_string(param_dict, [self.field_generic]),
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


# @filter_spec('url_portion_endswith', lambda field_to_test: isinstance(field_to_test, models.DateField))
# def muj_super_filtr(filterspec_instance): pass

def filter_spec(field_test_func):
    def fce(filter_func):
        name = '%s_%s' % (filter_func.__name__, CustomFilterSpec.__name__)
        cls = type(name, (CustomFilterSpec,), {})
        cls.filter_func = filter_func
        FilterSpec.register_insert(field_test_func, cls)
        return filter_func
    return fce
