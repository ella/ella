from django.http import HttpResponse
from django.db.models import Q
from ella.core.models import Category

def category_suggest_view(request, **kwargs):
    cat_begin = ''
    if 'q' in request:
        cat_begin = request['q']
    elif 'cat' in kwargs:
        cat_begin = kwargs['cat']
    start = cat_begin.strip()
    ft = []
    if len(start) > 0:
        lookup = Q(slug__startswith=start.lower()) | Q(title__startswith=start) | Q(tree_path__startswith=start.lower())
        data = Category.objects.filter(lookup)
        for item in data:
            ft.append(item.__unicode__().encode('utf-8'))
    res = HttpResponse('\n'.join(ft), mimetype='text/html;charset=utf-8')
    return res
