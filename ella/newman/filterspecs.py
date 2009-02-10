"""
Customized FilterSpecs.
"""
import logging

from django.utils.encoding import smart_unicode, iri_to_uri
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.contrib.admin.filterspecs import FilterSpec

from ella.ellaadmin.options import EllaModelAdmin
from ella.newman.views import customized_filter_view

log = logging.getLogger('ella.newman.filterspecs')
__registered_filter_urls = []


class StatefulFilterSpec(FilterSpec):
    """ stateful FilterSpec """
    def __init__(self, f, request, params, model, model_admin, field_path=None):
        self.state = 0
        self.params = params
        self.model = model
        self.model_admin = model_admin
        self.field_path = field_path
        super(StatefulFilterSpec, self).__init__(f, request, params, model, model_admin, field_path=field_path)
        log.debug('StatefulFilterSpec __init__')
        self.request_path_info = request.path_info

    def state1(self):
        raise NotImplementedError('state1 method should be overloaded (substituted at run-time).')

    def title(self):
        return self.field.verbose_name

    def choices(self, cl):
        log.debug('request: %s' % self.request_path_info)
        if self.request_path_info.endswith(self.url_end):
            log.debug('DateFieldFilter STATE 1')
            if self.state1():
                self.state = 1
        if self.state > 0:
            log.debug('DateFieldFilter returning choices')
            for title, param_dict in self.links:
                yield {'selected': self.date_params == param_dict,
                       'query_string': cl.get_query_string(param_dict, [self.field_generic]),
                       'display': title}
        else:
            log.debug('DateFieldFilter - No choices in state %d' % self.state)
#FilterSpec.register_insert(lambda f: isinstance(f, models.DateField), DateFieldFilterSpec)


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
FilterSpec.clean_registrations()


# 1. View funkce se registruje stale ta stejna pro kazde url stavu filtru.
# 2. Test na URL pro view bude pravdepodobne temer vzdy .endswith() ..tj. zase stejne.
# 3. choices() metoda filtru je stale stejne schema
# 4. Jedina "ziva" cast je metoda state1()
# ----------
# @filter_spec('url_portion_endswith', lambda field_to_test: isinstance(field_to_test, models.DateField))
# def muj_super_filtr(filterspec_instance): pass

def filter_spec(url_end, field_test_func):
    def fce(filter_func):
        if url_end in __registered_filter_urls:
            return None
        __registered_filter_urls.append(url_end)
        logging.debug(
            'Registering filter_func=%s , url_end=%s , field_test=%s' % (
                str(filter_func),
                url_end,
                str(field_test_func)
)
)
        filter_url_test = lambda p: p and p.endswith(url_end)
        EllaModelAdmin.register(filter_url_test, customized_filter_view)
        name = '%s_%s' % (filter_func.__name__, StatefulFilterSpec.__name__)
        cls = type(name, (StatefulFilterSpec,), {})
        cls.url_end = '%s/' % url_end
        cls.state1 = filter_func
        FilterSpec.register_insert(field_test_func, cls)
        return filter_func
    return fce

log.debug('Custom filters REGISTERED')
