from urllib import urlencode

from django import template
from django.template.loader import render_to_string
from django.utils.encoding import smart_str

register = template.Library()


def _do_paginator(context, adjacent_pages, template_name):
    if template_name is None:
        template_name = ('inclusion_tags/paginator.html',
                         'inc/paginator.html')
    else:
        template_name = ('inclusion_tags/paginator_%s.html' % template_name,
                         'inc/paginator_%s.html' % template_name)

    if not 'page' in context:
        # improper use of paginator tag, bail out
        return template_name, {}

    query_params = '?p='
    if 'request' in context:
        get = context['request'].GET
        query_params = '?%s&p=' % urlencode(dict((k, smart_str(v)) for (k, v) in get.iteritems() if k != 'p'))

    page = context['page']
    page_no = int(page.number)

    s = max(1, page_no - adjacent_pages - max(0, page_no + adjacent_pages -
        page.paginator.num_pages))
    page_numbers = range(s, min(page.paginator.num_pages, s + 2 * adjacent_pages) + 1)

    return template_name, {
        'query_params': query_params,
        'page': page,
        'results_per_page': page.paginator.per_page,
        'page_numbers': page_numbers,
        'show_first': 1 not in page_numbers,
        'show_last': page.paginator.num_pages not in page_numbers,
    }


@register.simple_tag(takes_context=True)
def paginator(context, adjacent_pages=2, template_name=None):
    """
    Renders a ``inclusion_tags/paginator.html`` or ``inc/paginator.html``
    template with additional pagination context. To be used in conjunction
    with the ``object_list`` generic
    view.

    If ``TEMPLATE_NAME`` parameter is given,
    ``inclusion_tags/paginator_TEMPLATE_NAME.html`` or 
    ``inc/paginator_TEMPLATE_NAME.html`` will be used instead.

    Adds pagination context variables for use in displaying first, adjacent pages and
    last page links in addition to those created by the ``object_list`` generic
    view.

    Taken from http://www.djangosnippets.org/snippets/73/

    Syntax::

        {% paginator [NUMBER_OF_ADJACENT_PAGES] [TEMPLATE_NAME] %}

    Examples::

        {% paginator %}
        {% paginator 5 %}
        {% paginator 5 "special" %}
        # with Django 1.4 and above you can also do:
        {% paginator template_name="special" %}
    """
    tname, context = _do_paginator(context, adjacent_pages, template_name)
    return render_to_string(tname, context)
