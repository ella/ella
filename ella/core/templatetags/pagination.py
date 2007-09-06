from django import template

register = template.Library()

def paginator(context, adjacent_pages=2):
    """
    To be used in conjunction with the object_list generic view.

    Adds pagination context variables for use in displaying first, adjacent_pages and
    last page links in addition to those created by the object_list generic
    view.

    """
    s = max(1, context["page"] - adjacent_pages - max(0, context["page"]+adjacent_pages-context["pages"]))
    page_numbers = range(s, min(context["pages"], s+2*adjacent_pages)+1)

    return {
        'hits': context['hits'],
        'results_per_page': context['results_per_page'],
        'page': context['page'],
        'pages': context['pages'],
        'page_numbers': page_numbers,
        'next': context['next'],
        'previous': context['previous'],
        'has_next': context['has_next'],
        'has_previous': context['has_previous'],
        'show_first': 1 not in page_numbers,
        'show_last': context['pages'] not in page_numbers,
}

register.inclusion_tag('inclusion_tags/paginator.html', takes_context=True)(paginator)

