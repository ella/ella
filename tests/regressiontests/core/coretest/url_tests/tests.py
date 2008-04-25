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

# sample object 1
>>> sm = SampleModel.objects.get(pk=1)
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
'\ncategory:example.com/,content_type:sample model,content_type_name:sample-models,object:SampleModel object,placement:SampleModel object placed in example.com/'


# sample object 2
>>> sm = SampleModel.objects.get(pk=2)
>>> sm.get_absolute_url()
'/2007/7/2/sample-models/first-object/'
>>> response = c.get('/2007/7/2/sample-models/first-object/')
>>> response.status_code
200
>>> response.context['object'] == sm
True
>>> response = c.get('/2007/7/2/sample-models/first-object/action/')
>>> response.status_code
200
>>> response.content
'\ncategory:example.com/,content_type:sample model,content_type_name:sample-models,object:SampleModel object,placement:SampleModel object placed in example.com/'

>>> response = c.get('/2007/7/1/sample-models/first-object/action/X/Y/Z/')
>>> response.status_code
200
>>> response.content
'X/Y/Z\ncategory:example.com/,content_type:sample model,content_type_name:sample-models,object:SampleModel object,placement:SampleModel object placed in example.com/'

>>> response = c.get('/2007/7/1/sample-models/first-object/otheraction/')
>>> response.status_code
404
>>> response = c.get('/2007/7/1/other-sample-models/first-other-object/otheraction/')
>>> response.status_code
200
>>> response.content
'\ncategory:example.com/,content_type:other sample model,content_type_name:other-sample-models,object:OtherSampleModel object,placement:OtherSampleModel object placed in example.com/'

# simple static listing
>>> response = c.get('/static/other-sample-models/first-other-object/')
>>> response.status_code
200
>>> response.content
'Sample detail:\ncategory:example.com/,content_type:other sample model,content_type_name:other-sample-models,object:OtherSampleModel object,placement:OtherSampleModel object placed in example.com/'
>>> response = c.get('/cat/subcat2/subsubcat/static/other-sample-models/first-other-object/otheraction/')
>>> response.status_code
200
>>> response.content
'\ncategory:example.com/cat/subcat2/subsubcat,content_type:other sample model,content_type_name:other-sample-models,object:OtherSampleModel object,placement:OtherSampleModel object placed in example.com/cat/subcat2/subsubcat'
'''

__test__ = {
    'base' : base,
    'custom' : custom,
}

if __name__ == '__main__':
    import doctest
    doctest.testmod()

