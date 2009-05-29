"""
paginator.py

Module intended to help with paginating QuerySet instances.
"""

from django.core.paginator import Paginator
from django.http import Http404

def get_page_no(request):
    if 'p' in request.GET and request.GET['p'].isdigit():
        return int(request.GET['p'])
    return 1

def paginate_qset(request, qset, items_per_page=25, exception_instance=Http404()):
    page_no = get_page_no(request)
    paginator = Paginator(qset, items_per_page)
    if page_no > paginator.num_pages or page_no < 1:
        raise exception_instance
    page = paginator.page(page_no)
    return {
        'page': page,
        'is_paginated': paginator.num_pages > 1,
        'results_per_page': items_per_page
    }
