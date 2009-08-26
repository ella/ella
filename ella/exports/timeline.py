from datetime import datetime, timedelta
import logging

from django.conf.urls.defaults import patterns, url
from django.utils.translation import ugettext_lazy as _
from django.forms import models as modelforms
from django import forms
from django.forms.fields import DateTimeField, IntegerField, HiddenInput
from django.core import signals as core_signals
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response

from ella.exports import models
from ella.exports.managers import ExportItemizer
from ella.utils import remove_diacritical

DATETIME_FORMAT = models.DATETIME_FORMAT
TIME_FORMAT = models.TIME_FORMAT
TIMELINE_STEP = timedelta(hours=2)  # two hours
log = logging.getLogger('ella.exports')

def get_timerange(year=datetime.now().year, month=datetime.now().month, day=datetime.now().day):
    now = datetime.now()
    out = list()
    for d in range(-2, 14):
        dt = timedelta(days=d)
        for h in [h for h in range(23) if h % 2 == 0]:
            t = datetime(year, month, day, h, 0) + dt
            str_t = t.strftime(DATETIME_FORMAT)
            out.append( (str_t, str_t) )
    return out

def get_export_choice_form():
    export_qs = models.Export.objects.all()
    exports = list()
    for e in export_qs:
        exports.append((e.slug, u'%s' % e,))

    timerange = get_timerange()

    class ExportChoiceForm(forms.Form):
        export_slug = forms.ChoiceField(choices=exports)
        range_from = forms.ChoiceField(choices=timerange)
        range_to = forms.ChoiceField(choices=timerange)
    log.debug('Form generated')
    return ExportChoiceForm

def get_timelined_items(slug, range_from, range_to, step=TIMELINE_STEP):
    itemizer = ExportItemizer(slug=slug)
    itemizer.datetime_from = range_from
    datetime_to = datetime.strptime(range_to, DATETIME_FORMAT)
    out = list()
    while itemizer.datetime_from <= datetime_to:
        column = list()
        column.append(itemizer.datetime_from.strftime(DATETIME_FORMAT))
        map(lambda x: column.append(x), itemizer)
        if not out or (out and out[-1] != column):
            log.debug(remove_diacritical('COLUMN: %s' % column))
            out.append(column)

        next_itemizer = ExportItemizer(slug=slug)
        next_itemizer.datetime_from = itemizer.datetime_from + step
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
                cell = None
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
    if 'export_slug' in request.GET:
        cx['export_form'] = FormClass(request.GET)
    else:
        cx['export_form'] = FormClass()
    if cx['export_form'].is_valid():
        log.debug('GENERATING EXPORT ITEMS')
        slug = request.GET['export_slug']
        range_from = request.GET['range_from']
        range_to = request.GET['range_to']
        items = get_timelined_items(slug, range_from, range_to)
        export = models.Export.objects.get(slug=slug)
        cx.update({
            'export': export,
            'timeline_table': reformat_list_for_table(items),
        })
    template_paths = [
        'newman/exports/timeline.html',
    ]
    if export:
        template_paths.append('exports/%s/timeline.html' % export.category.path)
        template_paths.append('newman/exports/%s/timeline.html' % export.category.path)
    template_paths.append('exports/timeline.html')
    return render_to_response(
        template_paths,
        cx
    )
