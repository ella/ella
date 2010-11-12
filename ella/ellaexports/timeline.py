from datetime import datetime, timedelta
import logging
from urllib import urlencode

from django.utils.translation import ugettext_lazy as _
from django import forms
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response

from ella.ellaexports import models
from ella.ellaexports.managers import ExportItemizer
from ella.utils import remove_diacritical
from ella.newman import utils, widgets
from ella.ellaexports.conf import ellaexports_settings

log = logging.getLogger('ella.exports')

def get_timerange(year=datetime.now().year, month=datetime.now().month, day=datetime.now().day):
    out = list()
    for d in range(-ellaexports_settings.RANGE_DAYS, ellaexports_settings.RANGE_DAYS):
        dt = timedelta(days=d)
        for h in [h for h in range(ellaexports_settings.DAY_MAX_HOUR) if h % ellaexports_settings.RANGE_WIDTH_HOURS == 0]:
            t = datetime(year, month, day, h, 0) + dt
            str_t = t.strftime(ellaexports_settings.DATETIME_FORMAT)
            out.append( (str_t, str_t) )
    return out

def get_export_choice_form():
    export_qs = models.Export.objects.all()
    exports = list()
    for e in export_qs:
        exports.append((e.slug, u'%s' % e,))

    #timerange = get_timerange()

    class ExportChoiceForm(forms.Form):
        export_slug = forms.ChoiceField(label=_('Export'), choices=exports)
        range_from = forms.DateTimeField(label=_('From'), widget=widgets.DateTimeWidget)
    log.debug('Form generated')
    return ExportChoiceForm

def get_timelined_items(slug, range_from, step=ellaexports_settings.TIMELINE_STEP):
    """
    @param  step  may contain timedelta object or list of timedelta objects.
    """
    itemizer = ExportItemizer(slug=slug)
    itemizer.datetime_from = range_from
    datetime_from = datetime.strptime(range_from, ellaexports_settings.DATETIME_FORMAT)
    datetime_to = datetime_from + timedelta(days=1)
    step_list = list()
    if type(step) in (list, tuple,):
        step_list = list(step)
        # in case of steps specified by timedelta list, first step should be set from it.
        itemizer.datetime_from = datetime_from + step_list.pop(0)

    out = list()
    while itemizer.datetime_from <= datetime_to:
        column = list()
        column.append(itemizer.datetime_from.strftime(ellaexports_settings.DATETIME_FORMAT))
        for i in itemizer:
            i.column_date_from = itemizer.datetime_from.strftime(ellaexports_settings.DATETIME_FORMAT)
            # add HitCounts
            if i.main_placement and i.main_placement.hitcount_set.count() > 0:
                i.hitcount = i.main_placement.hitcount_set.all()[0]
            column.append(i)
        if not out or (out and out[-1] != column):
            while (len(column) - 1) < itemizer.export.max_visible_items:
                column.append(ellaexports_settings.EMPTY_TIMELINE_CELL)
            log.debug(remove_diacritical('COLUMN: %s' % column))
            out.append(column)

        next_itemizer = ExportItemizer(slug=slug)
        if type(step) == timedelta:
            next_itemizer.datetime_from = itemizer.datetime_from + step
        elif type(step) in (list, tuple,):
            if not step_list:
                break
            next_itemizer.datetime_from = datetime_from + step_list.pop(0) # ..mmm pop, tadadaaa.. from beginning of the list.
        else:
            raise AttributeError('Wrong data type of step arg. step must be timedelta, list or tuple type.')
        itemizer = next_itemizer

    return out

def reformat_list_for_table(list_data):
    max_rows = 0
    for column in list_data:
        # find deepest column (max rows in table)
        if len(column) > max_rows:
            max_rows = len(column)
    table = list()
    for row_index in range(max_rows):
        table_row = list()
        for column in list_data:
            if len(column) > row_index:
                cell = column[row_index]
            else:
                cell = ellaexports_settings.EMPTY_TIMELINE_CELL
            table_row.append(cell)
        table.append(table_row)
    return table

def timeline_view(request, extra_context=None):
    """
    Returns timeline view (more powerful interface to maintain export positions).

    Timeline view should look like this:

        | 8:00 - 10:00  | 10:00 - 12:00  | 12:00 - 14:00    |
    ----+---------------+----------------+------------------+ etc...
     #1 | Exported item | Ex. item #2    |  E.i.#3 | E.i.#4 |
    ----+---------------+----------------+------------------+
     #2 | ...

    (first column is export position shown at time specified by following column.
     Exported positions (Articles, Galleries, etc.) are shown in cells below first row.)

    Time window can be set optionaly by set of combo boxes (i.e. from 1 P.M. to 4 P.M.)

    ----

    Timeline data given to template structure:
    [
        [first column item, ..., n-th column item], # 1st row
        [first column item, ..., n-th column item], # 2nd row
    ]
    """

    export = None
    cx = dict()
    FormClass = get_export_choice_form()
    request_data = request.GET
    if 'show' not in request_data and 'export_slug' in request_data:
        new_path = (
            request.path,
            '?',
            'show=1&',
            urlencode(request_data)
        )
        return utils.JsonResponseRedirect(''.join(new_path))
    elif 'show' in request_data and 'export_slug' in request_data:
        cx['export_form'] = FormClass(request_data)
    else:
        cx['export_form'] = FormClass()
    if cx['export_form'].is_valid():
        log.debug('GENERATING EXPORT ITEMS')
        slug = request_data['export_slug']
        range_from = request_data['range_from']
        items = get_timelined_items(slug, range_from)
        export = models.Export.objects.get(slug=slug)
        cx.update({
            'export': export,
            #'timeline_table': reformat_list_for_table(items),
            'timeline_data': items,
            'title': 'Timeline for "%s" (%s)' % (slug, range_from)
        })
    template_paths = [
        'newman/ellaexports/timeline.html',
    ]
    if export:
        template_paths.append('ellaexports/%s/timeline.html' % export.category.path)
        template_paths.append('newman/ellaexports/%s/timeline.html' % export.category.path)
    template_paths.append('ellaexports/timeline.html')
    return render_to_response(
        template_paths,
        cx
    )

def append_view(request, **kwargs):
    " Wrapper to timeline_insert_append_view(). "
    position = kwargs.get('position', None)
    if position and type(position) in [str, unicode] and position.isdigit():
        position = int(position) + 1
        kwargs['position'] = position
    return timeline_insert_append_view(request, **kwargs)

def insert_view(request, **kwargs):
    " Wrapper to timeline_insert_append_view(). "
    position = kwargs.get('position', None)
    if position and type(position) in [str, unicode] and position.isdigit():
        position = int(position) - 1
        kwargs['position'] = position
    return timeline_insert_append_view(request, **kwargs)

def timeline_insert_append_view(request, **kwargs):
    """
    Inserts/appends export element before/after an item (via ExportPosition and ExportMeta).

    Keyword arguments:
    @param   id_item     Existing Publishable object placed after new inserted item.
    @param   position    ExportPosition object's position.
    @param   id_export   Export object id.
    @param   id_publishable  Chosen Publishable object to be associated with new ExportMeta object.

    1. get Export object associated with item.
    2. create ExportMeta for item.
    3. create ExportPosition for ExportMeta. Preset datetime visible_from and visible_to.
    """
    position = kwargs.get('position', None)
    id_item = kwargs.get('id_item', None)
    id_export = kwargs.get('id_export', None)
    visible_from = kwargs.get('visible_from', None)
    id_publishable = kwargs.get('id_publishable', None)

    if not (id_item and id_export and id_publishable and position and visible_from):
        raise AttributeError
    meta = models.ExportMeta.objects.create(
        #publishable=Publishable.objects.get(pk=id_publishable),
        publishable_id=id_publishable
    )
    date_from = datetime.strptime(visible_from, ellaexports_settings.DATETIME_FORMAT)
    visible_to = (date_from + ellaexports_settings.TIMELINE_STEP - timedelta(seconds=-1)).strftime(ellaexports_settings.DATETIME_FORMAT)
#?exportposition_set-0-position=2&exportposition_set-0-visible_to=2009-08-01 20:00&exportposition_set-0-visible_from=2008-08-01 18:00
    url_parts = {
        'id_exportposition_set-0-position': int(position),
        'id_exportposition_set-0-visible_from': visible_from,
        'id_exportposition_set-0-visible_to': visible_to,
        'id_exportposition_set-0-export': int(id_export),
        'http_redirect_to': request.GET.get('http_redirect_to', '')
    }
    address = '%s?%s' % (
        reverse('newman:exports_exportmeta_change', args=[meta.pk]),
        urlencode(url_parts)
    )
    return utils.JsonResponseRedirect(address)


