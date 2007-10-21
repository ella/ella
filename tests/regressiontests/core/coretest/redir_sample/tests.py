base = r'''
>>> from django.test.client import Client
>>> c = Client()
>>> response = c.get('/')
>>> response.status_code
200
>>> response.template.name
'page/category.html'
>>> response.context['category']
<Category: example.com/>

>>> from redir_sample.models import RedirObject
>>> o1 = RedirObject.objects.get(pk=1)
>>> o1.get_absolute_url()
'/2007/7/1/redir-objects/redirobject-1/'
>>> response = c.get('/2007/7/1/redir-objects/redirobject-1/')
>>> response.status_code
200
>>> response.context['object'] == o1
True
>>> o1.slug = 'redirobject-1-altered'
>>> o1.save()
>>> o1.get_absolute_url()
'/2007/7/1/redir-objects/redirobject-1-altered/'
>>> response = c.get('/2007/7/1/redir-objects/redirobject-1/')
>>> response.status_code
301
>>> response['Location']
'/2007/7/1/redir-objects/redirobject-1-altered/'
>>> response = c.get('/2007/7/1/redir-objects/redirobject-1-altered/')
>>> response.status_code
200
>>> response.context['object'] == o1
True
>>> from django.contrib.redirects.models import Redirect
>>> Redirect.objects.all()
[<Redirect: /2007/7/1/redir-objects/redirobject-1/ ---> /2007/7/1/redir-objects/redirobject-1-altered/>]
>>> o1.slug = 'redirobject-1-altered-twice'
>>> o1.save()
>>> response = c.get('/2007/7/1/redir-objects/redirobject-1/')
>>> response.status_code
301
>>> response['Location']
'/2007/7/1/redir-objects/redirobject-1-altered-twice/'
>>> Redirect.objects.all()
[<Redirect: /2007/7/1/redir-objects/redirobject-1-altered/ ---> /2007/7/1/redir-objects/redirobject-1-altered-twice/>, <Redirect: /2007/7/1/redir-objects/redirobject-1/ ---> /2007/7/1/redir-objects/redirobject-1-altered-twice/>]

>>> o1.delete()
>>> Redirect.objects.all()
[]
>>> response = c.get('/2007/7/1/redir-objects/redirobject-1-altered/')
>>> response.status_code
404
>>> response = c.get('/2007/7/1/redir-objects/redirobject-1/')
>>> response.status_code
404

'''

__test__ = {
    'base' : base,
}

if __name__ == '__main__':
    import doctest
    doctest.testmod()

