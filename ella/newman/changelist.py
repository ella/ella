import logging

from django.contrib.admin.views.main import *

log = logging.getLogger('ella.newman')

class FilterableChangeList(ChangeList):

    def is_filtered(self):
        """ Iterates over all ChangeList's filters. Returns True if at least one filter is active. """
        if not hasattr(self, '_filters'):
            return False
        #sql, param_list = self.query_set.query.where.as_sql()
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
