from django.views.static import serve
from django.http import Http404


def fallback_serve(request, path, document_roots=()):
    """
    try to serve static content from one directory,
    if it is not found there, try another one
    """
    for d in document_roots:
        try:
            return serve(request, path, document_root=d, show_indexes=True)
        except Http404:
            continue
    raise Http404('Document "%s" not found in any base directory (%s).' % (path, document_roots))

