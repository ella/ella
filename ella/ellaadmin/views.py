from django.http import HttpResponse
from django.db.models import Q
from ella.core.models import Category, Author

def category_suggest_view(request, **kwargs):
    cat_begin = ''
    if 'q' in request:
        cat_begin = request['q']
    elif 'cat' in kwargs:
        cat_begin = kwargs['cat']
    start = cat_begin.strip().lower()
    ft = []
    if len(start) > 1:
        lookup = Q(slug__startswith=start) | Q(title__istartswith=start) | Q(tree_path__startswith=start)
        data = Category.objects.filter(lookup).values('site__name','tree_path',)
        for item in data:
            ft.append("%s:%s".encode('utf-8') % (item['site__name'], item['tree_path']))
    return HttpResponse('\n'.join(ft), mimetype='text/html;charset=utf-8')

def author_suggest_view(request, **kwargs):
    beg = ''
    if 'q' in request:
        beg = request['q']
    elif 'a' in kwargs:
        beg = kwargs['a']
    start = beg.strip().lower()
    ft = []
    if len(start) > 1:
        lookup = Q(slug__startswith=start) | Q(name__icontains=start)
        data = Author.objects.filter(lookup).values('pk','name',)
        for item in data:
            ft.append("%s:%s".encode('utf-8') % (item['pk'], item['name']))
    return HttpResponse('\n'.join(ft), mimetype='text/html;charset=utf-8')
