import logging

from django.contrib.admin.views.main import *

log = logging.getLogger('ella.newman')

class FilterableChangeList(ChangeList):

    def is_filtered(self):
        """ Iterates over all ChangeList's filters. Returns True if at least one filter is active. """
        if not hasattr(self, '_filters'):
            return False
        for f in self._filters:
            act = f.is_active(self.params)
            log.debug('is_active=%s for filter %s:' % (act, f))
            if act:
                return True
        return False

class NewmanChangeList(FilterableChangeList):
    """ Overridden ChangeList without filter initialization (filters do all SQL during init) """
    def __init__(self, request, model, list_display, list_display_links, list_filter, date_hierarchy, search_fields, list_select_related, list_per_page, list_editable, model_admin):
        super(NewmanChangeList, self).__init__(request, model, list_display, list_display_links, list_filter, date_hierarchy, search_fields, list_select_related, list_per_page, list_editable, model_admin)


    def get_filters(self, request):
        self._filters, status = super(NewmanChangeList, self).get_filters(request)
        return [], False


class FilterChangeList(FilterableChangeList):
    """ Changelist intended to be used with filter view. (makes only necessary SQL for filter choices). """
    def __init__(self, request, model, list_display, list_display_links, list_filter, date_hierarchy, search_fields, list_select_related, list_per_page, list_editable, model_admin):
        self.model = model
        self.opts = model._meta
        self.lookup_opts = self.opts
        self.list_display = list_display
        self.list_display_links = list_display_links
        self.list_filter = list_filter
        self.date_hierarchy = date_hierarchy
        self.search_fields = search_fields
        self.list_select_related = list_select_related
        self.list_per_page = list_per_page
        self.list_editable = list_editable
        self.model_admin = model_admin
        self.is_popup = IS_POPUP_VAR in request.GET


        self.title = (ugettext('Select %s') % force_unicode(self.opts.verbose_name) or ugettext('Select %s to change') % force_unicode(self.opts.verbose_name))
        self.params = dict(request.GET.items())
        self.filter_specs, self.has_filters = self.get_filters(request)

    def get_filters(self, request):
        filter_specs = []
        if self.list_filter:
            lookup_opts = self.lookup_opts
            for filter_name in self.list_filter:
                if '__' in filter_name:
                    f = None
                    model = self.model
                    path = filter_name.split('__')
                    for field_name in path[:-1]:
                        f = model._meta.get_field(field_name)
                        model = f.rel.to
                        f = model._meta.get_field(path[-1])
                        spec = FilterSpec.create(f, request, self.params, model, self.model_admin, field_path=filter_name)
                else:
                    f = lookup_opts.get_field(filter_name)
                    spec = FilterSpec.create(f, request, self.params, self.model, self.model_admin)
                if spec and spec.has_output():
                    filter_specs.append(spec)
        if hasattr(self.model_admin, 'unbound_list_filter'):
            for klass in self.model_admin.unbound_list_filter:
                spec = klass(None, request, self.params, self.model, self.model_admin)
                if spec and spec.has_output():
                    filter_specs.append(spec)
        return filter_specs, bool(filter_specs)
