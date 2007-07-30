base = r'''
>>> from django.test.client import Client
>>> c = Client()

# category homepages
>>> from ella.core.models import Category
>>> for cat in Category.objects.all():
...     response = c.get(cat.get_absolute_url())
...     if response.status_code != 200:
...         print 'KO'
...     if response.context['category'] != cat:
...         print 'KO'
>>> response = c.get('/')
>>> response.status_code
200
>>> response.context['category'].tree_parent

# various listings
>>> c.get('/2007/categories/').status_code
200
>>> c.get('/2007/01/categories/').status_code
200
>>> c.get('/2007/01/01/categories/').status_code
200
>>> c.get('/2007/01/01/').status_code
200
>>> c.get('/2007/01/').status_code
200
>>> c.get('/2007/').status_code
200

'''

__test__ = {
    'base' : base,
}

if __name__ == '__main__':
    import doctest
    doctest.testmod()

