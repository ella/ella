"""
Customized FilterSpecs.
"""
import datetime
from time import time
import logging

from django.utils.encoding import smart_unicode, iri_to_uri
from django.utils.translation import ugettext as _
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.contrib.admin.filterspecs import FilterSpec
from django.db import models

log = logging.getLogger('ella.newman.filterspecs')

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


class DateFieldFilterSpec(FilterSpec):
    """ stateful FilterSpec """
    def __init__(self, f, request, params, model, model_admin, field_path=None):
        self.state = 0
        self.params = params
        self.model = model
        self.model_admin = model_admin
        self.field_path = field_path
        super(DateFieldFilterSpec, self).__init__(f, request, params, model, model_admin, field_path=field_path)
        log.debug('DateFieldFilter __init__')
        log.debug('request: %s' % request.path_info)
        if request.path_info.endswith('filter_date/'):
            self.state1()

    def state1(self):
        log.debug('DateFieldFilter STATE 1')
        params = self.params; model = self.model; model_admin = self.model_admin; field_path = self.field_path
        self.field_generic = '%s__' % self.field_path
        self.date_params = dict([(k, v) for k, v in params.items() if k.startswith(self.field_generic)])
        today = datetime.date.today()
        one_week_ago = today - datetime.timedelta(days=7)
        today_str = isinstance(self.field, models.DateTimeField) and today.strftime('%Y-%m-%d 23:59:59') or today.strftime('%Y-%m-%d')

        self.links = (
            (_('Any date'), {}),
            (_('Today'), {'%s__year' % self.field_path: str(today.year),
                       '%s__month' % self.field_path: str(today.month),
                       '%s__day' % self.field_path: str(today.day)}),
            (_('Past 7 days'), {'%s__gte' % self.field_path: one_week_ago.strftime('%Y-%m-%d'),
                             '%s__lte' % self.field_path: today_str}),
            (_('This month'), {'%s__year' % self.field_path: str(today.year),
                             '%s__month' % self.field_path: str(today.month)}),
            (_('This year'), {'%s__year' % self.field_path: str(today.year)})
)
        self.state = 1

    def title(self):
        return self.field.verbose_name

    def choices(self, cl):
        if self.state > 0:
            log.debug('DateFieldFilter returning choices')
            for title, param_dict in self.links:
                yield {'selected': self.date_params == param_dict,
                       'query_string': cl.get_query_string(param_dict, [self.field_generic]),
                       'display': title}
        else:
            log.debug('DateFieldFilter - No choices in state %d' % self.state)

FilterSpec.register_insert(lambda f: isinstance(f, models.DateField), DateFieldFilterSpec)

log.debug('Custom filters REGISTERED')
