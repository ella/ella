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
>>> response.context['category'].tree_parent is None
True

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

custom = r'''
# custom url dispatching
>>> from django.test.client import Client
>>> c = Client()
>>> from url_tests.models import SampleModel, register_urls
>>> register_urls()
>>> sm = SampleModel.objects.all()[0]
>>> sm.get_absolute_url()
'/2007/7/1/sample-models/first-object/'
>>> response = c.get('/2007/7/1/sample-models/first-object/')
>>> response.status_code
200
>>> response.context['object'] == sm
True
>>> response = c.get('/2007/7/1/sample-models/first-object/action/')
>>> response.status_code
200
>>> response.content
'\ncategory:Home Page,content_type_name:sample-models,object:SampleModel object,content_type:sample model,listing:SampleModel object listed in Home Page'

>>> response = c.get('/2007/7/1/sample-models/first-object/action/X/Y/Z/')
>>> response.status_code
200
>>> response.content
'X/Y/Z\ncategory:Home Page,content_type_name:sample-models,object:SampleModel object,content_type:sample model,listing:SampleModel object listed in Home Page'

>>> response = c.get('/2007/7/1/sample-models/first-object/otheraction/')
>>> response.status_code
404
>>> response = c.get('/2007/7/1/other-sample-models/first-other-object/otheraction/')
>>> response.status_code
200
>>> response.content
'\ncategory:Home Page,content_type_name:other-sample-models,object:OtherSampleModel object,content_type:other sample model,listing:OtherSampleModel object listed in Home Page'
'''

__test__ = {
    'base' : base,
    'custom' : custom
}

if __name__ == '__main__':
    import doctest
    doctest.testmod()

